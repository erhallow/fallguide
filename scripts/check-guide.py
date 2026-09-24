#!/usr/bin/env python3
"""Read-only regression checks for the approved static fall-guide edits."""

from collections import Counter
from html.parser import HTMLParser
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "index.html").read_text()
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}


class Node:
    def __init__(self, tag, attrs=(), parent=None):
        self.tag, self.attrs, self.parent = tag, dict(attrs), parent
        self.children = []
        self.text = ""

    def has_class(self, name):
        return name in self.attrs.get("class", "").split()

    def descendants(self):
        for child in self.children:
            yield child
            yield from child.descendants()


class Document(HTMLParser):
    def __init__(self, markup):
        super().__init__(convert_charrefs=True)
        self.root = Node("document")
        self.stack = [self.root]
        self.feed(markup)
        self.nodes = list(self.root.descendants())

    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs, self.stack[-1])
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


DOC = Document(HTML)


class GuideChecks(unittest.TestCase):
    def by_id(self, value):
        return next(n for n in DOC.nodes if n.attrs.get("id") == value)

    def listing(self, value):
        return next(n for n in DOC.nodes if n.attrs.get("data-audit-id") == str(value))

    def hrefs(self, node):
        return [n.attrs["href"] for n in node.descendants() if n.tag == "a"]

    def test_document_landmarks_and_internal_targets(self):
        self.assertEqual(sum(n.tag == "h1" for n in DOC.nodes), 1)
        self.assertEqual(sum(n.tag == "main" for n in DOC.nodes), 1)
        self.assertEqual(self.by_id("main-content").attrs.get("tabindex"), "-1")
        ids = Counter(n.attrs["id"] for n in DOC.nodes if "id" in n.attrs)
        self.assertFalse([key for key, count in ids.items() if count != 1])
        for node in DOC.nodes:
            for key in ("href", "xlink:href"):
                value = node.attrs.get(key, "")
                if value.startswith("#"):
                    self.assertIn(value[1:], ids)
            for value in node.attrs.get("aria-labelledby", "").split():
                self.assertIn(value, ids)

    def test_placeholders_are_not_subscription_forms(self):
        slots = [n for n in DOC.nodes if n.has_class("sub-slot")]
        self.assertEqual(len(slots), 2)
        for slot in slots:
            self.assertIn("Signup form goes here", slot.text)
            self.assertFalse(any(n.tag in {"form", "input", "button", "iframe"} for n in slot.descendants()))
        self.assertNotIn("printable", DOC.root.text.lower())
        self.assertNotIn("download the guide", DOC.root.text.lower())

    def test_reminders_are_static_with_four_completed(self):
        reminders = [n for n in self.by_id("todos").descendants() if n.tag == "li"]
        self.assertEqual(len(reminders), 12)
        self.assertEqual(sum(n.has_class("is-done") for n in reminders), 4)
        self.assertEqual(sum(n.tag == "s" for n in self.by_id("todos").descendants()), 4)
        for node in self.by_id("todos").descendants():
            self.assertNotIn(node.tag, {"input", "button", "a"})
            self.assertNotIn("onclick", node.attrs)
            self.assertNotIn("tabindex", node.attrs)
        self.assertNotIn("localStorage", HTML)
        self.assertNotIn("sessionStorage", HTML)

    def test_inventory_and_source_notes(self):
        cards = [n for n in DOC.nodes if n.has_class("card")]
        self.assertEqual(len(cards), 44)
        self.assertEqual(sum(n.has_class("hcard") for n in cards), 14)
        for card in cards:
            self.assertTrue(any(n.has_class("source-note") for n in card.descendants()))
        present = {n.attrs.get("data-audit-id") for n in DOC.nodes}
        self.assertTrue({str(i) for i in range(95, 139)} <= present)
        self.assertTrue({"44", "47", "94"}.isdisjoint(present))

    def test_corrected_link_destinations(self):
        expected = {
            23: "https://fofarms.com/harvest-season/",
            24: "https://fofarms.com/harvest-season/pumpkin-smash-bash/",
            41: "https://www.pnw.edu/event/acorn-concert-series-sarahs-place-zach-bryan-and-noah-kahan-tribute/",
            42: "https://www.valparaisoevents.com/event/valparaisouniversitysymphonyorchestrahalloweenspooktacular",
            43: "https://www.journeyman.com/events/halloween-party-valparaiso-in-26/",
            45: "https://brickartlive.com/event/without-u2-driver-8-tributes-to-u2-r-e-m/",
            46: "https://www.eventbrite.com/e/halloween-bash-26-nwi-adult-halloween-party-costume-contest-tickets-1993982098132",
            33: "https://friendshipbotanicgardens.org/event/haunted-trails-event-2026/",
            79: "https://www.facebook.com/events/1536607871566699",
            102: "https://friendshipbotanicgardens.org/event/haunted-trails-event-2026/",
        }
        for listing_id, url in expected.items():
            self.assertEqual(self.hrefs(self.listing(listing_id))[0], url)
        self.assertEqual(len(self.hrefs(self.listing(130))), 2)

    def test_aperion_event_details_are_verified(self):
        listing = self.listing(79)
        self.assertIn("October 22, 4–6 p.m. Central", listing.text)
        self.assertIn("1101 E. Coolspring Avenue", listing.text)
        self.assertIn("Public trunk-or-treat", listing.text)
        notes = [n.text for n in listing.descendants() if n.has_class("source-note")]
        self.assertEqual(notes, ["2026 date and time verified from organizer event page."])
        self.assertNotIn("A dated event announcement is needed", listing.text)
        self.assertNotIn("2026 details not verified", listing.text)

    def test_historical_and_current_town_hours_are_separate(self):
        town_section = self.by_id("town-hours")
        tiles = [n for n in town_section.descendants() if n.has_class("tile")]
        self.assertEqual(len(tiles), 31)
        for tile in tiles:
            self.assertIn("2025", tile.text)
            self.assertIn("2026", tile.text)
            self.assertTrue(self.hrefs(tile))
        confirmed = next(n for n in town_section.descendants() if n.has_class("confirmed-town"))
        self.assertIn("Knox", confirmed.text)
        self.assertIn("5:30–7 p.m. Central Time", confirmed.text)
        self.assertIn("https://www.cityofknox.net/", self.hrefs(confirmed))

    def test_no_unverified_event_schema(self):
        schemas = [json.loads(n.text) for n in DOC.nodes if n.attrs.get("type") == "application/ld+json"]
        self.assertEqual(len(schemas), 1)
        self.assertEqual(schemas[0]["@type"], "CollectionPage")
        self.assertNotIn('"@type": "Event"', HTML)
        self.assertEqual(schemas[0]["url"], "https://fallguide.nwiexplored.com/")

    def test_footer_and_chart_alternatives_exist(self):
        footer = next(n for n in DOC.nodes if n.tag == "footer")
        self.assertIn("https://nwiexplored.com/", self.hrefs(footer))
        self.assertIn("#p1", self.hrefs(footer))
        for chart_id in ("sunchart", "vine"):
            chart = self.by_id(chart_id)
            self.assertEqual(chart.attrs.get("role"), "img")
            self.assertTrue(chart.attrs.get("aria-label"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
