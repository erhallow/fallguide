#!/usr/bin/env python3
"""Label guide links. Read-only by default; --patch prints an apply_patch patch."""

import argparse
from collections import Counter
import difflib
from html import escape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import unicodedata
from urllib.parse import unquote_plus, urlencode

ROOT = Path(__file__).resolve().parents[1]
UTMS = {"utm_source": "nwi_explored", "utm_medium": "referral", "utm_campaign": "fall_guide_2026"}
MANAGED = {*UTMS, "utm_content"}
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
CHAPTERS = {"p1": "intro", "p2": "events", "p3": "halloween", "p4": "outdoors"}
PANELS = {"tr-h": "community-trick-or-treating", "hh-h": "haunted-attractions-and-ghost-tours",
          "pp-h": "pumpkin-patches-and-apple-orchards", "hk-h": "fall-color-walks-and-hikes"}


class Node:
    def __init__(self, tag, attrs=(), parent=None, offset=0, raw=""):
        self.tag, self.attrs, self.parent = tag, dict(attrs), parent
        self.offset, self.raw, self.children, self.text = offset, raw, [], ""

    def has_class(self, name):
        return name in self.attrs.get("class", "").split()

    def descendants(self):
        for child in self.children:
            yield child
            yield from child.descendants()

    def ancestors(self):
        node = self.parent
        while node:
            yield node
            node = node.parent


class Document(HTMLParser):
    def __init__(self, markup):
        super().__init__(convert_charrefs=True)
        self.lines = [0]
        for match in re.finditer("\n", markup):
            self.lines.append(match.end())
        self.root = Node("document")
        self.stack = [self.root]
        self.feed(markup)
        self.nodes = list(self.root.descendants())

    def handle_starttag(self, tag, attrs):
        line, col = self.getpos()
        node = Node(tag, attrs, self.stack[-1], self.lines[line - 1] + col, self.get_starttag_text())
        self.stack[-1].children.append(node)
        if tag not in VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                break

    def handle_data(self, data):
        for node in self.stack:
            node.text += data


def slug(text):
    text = unicodedata.normalize("NFKD", text.replace("&", " and "))
    text = text.encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def strip_utm(url):
    """Do not decode/re-encode destination queries (Facebook IDs, signed URLs, etc.)."""
    base, hashmark, fragment = url.partition("#")
    path, question, query = base.partition("?")
    fields = [field for field in query.split("&")
              if unquote_plus(field.partition("=")[0]).lower() not in MANAGED]
    return path + (question + "&".join(fields) if fields and fields != [""] else "") + hashmark + fragment


def tagged_url(url, section, item, link):
    base, hashmark, fragment = strip_utm(url).partition("#")
    separator = "&" if "?" in base else "?"
    return base + separator + urlencode({**UTMS, "utm_content": f"{section}__{item}__{link}"}) + hashmark + fragment


def labels(anchor):
    ancestors = list(anchor.ancestors())
    panel = next((n for n in ancestors if n.tag == "section" and not n.has_class("sheet")), None)
    chapter = next((CHAPTERS[n.attrs["id"]] for n in ancestors if n.attrs.get("id") in CHAPTERS), None)
    title = anchor.attrs.get("aria-label") or anchor.text.strip()
    if anchor.has_class("brand-link"):
        return f"{chapter}-header", "nwi-explored", "newsletter-home"
    if any(n.tag == "footer" for n in ancestors):
        return "footer", "nwi-explored", "sample-issue" if "/p/" in anchor.attrs["href"] else "newsletter-home"
    if panel and panel.attrs.get("id") in {"subscribe", "subscribe-bottom"}:
        return "newsletter-top" if panel.attrs["id"] == "subscribe" else "newsletter-bottom", "nwi-explored", "sample-issue" if "/p/" in anchor.attrs["href"] else "newsletter-home"
    if not panel:
        raise ValueError(f"Unclassified link: {title}")
    panel_id = panel.attrs.get("aria-labelledby")
    if panel_id == "tt-h":
        town = next(n for n in ancestors if n.has_class("tile") or n.has_class("confirmed-town"))
        name = next(n.text for n in town.descendants() if n.has_class("tn") or n.tag == "h3").split(" · ")[0]
        section = "town-trick-or-treat-hours-2026" if town.has_class("confirmed-town") else "town-trick-or-treat-hours-2025-reference"
        return section, slug(name), slug(title)
    if panel_id == "ev-h":
        groups = [n for n in panel.descendants() if n.tag == "h3" and n.offset < anchor.offset]
        section = slug(groups[-1].text)
    else:
        section = PANELS[panel_id]
    listing = next((n for n in ancestors if n.tag == "li" or n.has_class("card")), None)
    if not listing:
        return section, slug(title), "details"
    heading = next((n for n in listing.descendants() if any(n.has_class(c) for c in ("ev-title", "cn", "n"))), None)
    if heading and not heading.has_class("cn"):
        heading = next((n for n in heading.descendants() if n.tag == "a"), heading)
    if heading is None:
        heading = next(n for n in listing.descendants() if n.tag == "a")
    item = slug(heading.text)
    link = "details" if slug(title) == item else slug(title)
    return section, item, link


def tag_document(markup):
    doc, replacements, inventory = Document(markup), [], []
    for anchor in doc.nodes:
        if anchor.tag != "a" or not re.match(r"https?://", anchor.attrs.get("href", ""), re.I):
            continue
        section, item, link = labels(anchor)
        assert section and item and link
        assert len(item + "__" + link) <= 255, (item, link)
        href = tagged_url(anchor.attrs["href"], section, item, link)
        raw = re.sub(r'\s+data-guide-(section|item|link)="[^"]*"', "", anchor.raw)
        raw = re.sub(r'\bhref="[^"]*"', lambda _: 'href="' + escape(href, quote=True) + '"', raw, count=1)
        raw = raw[:-1] + f' data-guide-section="{section}" data-guide-item="{item}" data-guide-link="{link}">'
        replacements.append((anchor.offset, len(anchor.raw), raw))
        inventory.append({"section": section, "item": item, "link": link, "url": href})
    for start, size, raw in reversed(replacements):
        markup = markup[:start] + raw + markup[start + size:]
    return markup, inventory


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--patch", action="store_true")
    mode.add_argument("--inventory", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    original = (ROOT / "index.html").read_text()
    updated, inventory = tag_document(original)
    if args.patch:
        if updated != original:
            diff = list(difflib.unified_diff(original.splitlines(True), updated.splitlines(True), n=1))
            print("*** Begin Patch\n*** Update File: " + str(ROOT / "index.html"))
            for line in diff[2:]:
                print("@@" if line.startswith("@@") else line.rstrip("\n"))
            print("*** End Patch")
    elif args.inventory:
        print(json.dumps(inventory, indent=2))
    else:
        print(json.dumps(dict(sorted(Counter(row["section"] for row in inventory).items())), indent=2))
        print(f"{len(inventory)} outgoing web links")
        if updated != original:
            raise SystemExit("Labels need updating: review and apply the output of --patch.")
        print("PASS: all labels current; regeneration is idempotent.")


if __name__ == "__main__":
    main()
