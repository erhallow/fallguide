#!/usr/bin/env python3
"""Offline tests for static link labels; never contact event sites or analytics."""
from collections import Counter
from pathlib import Path
import unittest
from urllib.parse import parse_qs, urlsplit

from tag_links import Document, UTMS, labels, strip_utm, tag_document, tagged_url

HTML = (Path(__file__).resolve().parents[1] / "index.html").read_text()
DOC = Document(HTML)
LINKS = [n for n in DOC.nodes if n.tag == "a" and n.attrs.get("href", "").startswith(("http://", "https://"))]


class TrackingChecks(unittest.TestCase):
    def test_every_web_link_has_consistent_static_labels(self):
        self.assertEqual(len(LINKS), 181)
        identities = []
        for link in LINKS:
            with self.subTest(link=link.text):
                section, item, variant = labels(link)
                self.assertEqual(link.attrs["data-guide-section"], section)
                self.assertEqual(link.attrs["data-guide-item"], item)
                self.assertEqual(link.attrs["data-guide-link"], variant)
                query = parse_qs(urlsplit(link.attrs["href"]).query)
                for key, value in {**UTMS, "utm_content": f"{section}__{item}__{variant}"}.items():
                    self.assertEqual(query[key], [value])
                self.assertLessEqual(len(item + "__" + variant), 255)
                identities.append((section, item, variant))
        self.assertEqual(len(set(identities)), len(identities))

    def test_internal_phone_svg_and_metadata_not_tagged(self):
        for node in DOC.nodes:
            if node not in LINKS:
                self.assertFalse(any(key.startswith("data-guide-") for key in node.attrs))
                self.assertNotIn("utm_", node.attrs.get("href", ""))
        schemes = Counter(n.attrs["href"].split(":")[0] for n in DOC.nodes if n.tag == "a" and n not in LINKS)
        self.assertEqual(schemes["tel"], 2)

    def test_regeneration_does_not_change_anything(self):
        self.assertEqual(tag_document(HTML)[0], HTML)

    def test_queries_fragments_and_encoding_are_preserved(self):
        for base in [
            "https://example.org/path",
            "https://example.org/path#tickets",
            "https://example.org/path?fbid=123&set=pb.100.-2207520000#photo",
            "https://example.org/picked-%26-u-pick?url=x%2Fy%26z&query=hello%20world&x=1&x=2#A%20B",
            "https://example.org/Calendar.aspx?EID=565",
            "https://example.org/map.pdf?language_id=1",
        ]:
            with self.subTest(url=base):
                tagged = tagged_url(base, "section", "item", "details")
                self.assertEqual(strip_utm(tagged), base)
                self.assertEqual(tagged_url(tagged, "section", "item", "details"), tagged)

    def test_existing_managed_utms_replaced_not_duplicated(self):
        base = "https://example.org/?x=a%20b&utm_source=old&utm_content=old&utm_source=again#details"
        tagged = tagged_url(base, "section", "item", "details")
        self.assertEqual(strip_utm(tagged), "https://example.org/?x=a%20b#details")
        self.assertEqual(parse_qs(urlsplit(tagged).query)["utm_source"], [UTMS["utm_source"]])

    def test_special_items_and_duplicate_destinations(self):
        wildlife = next(n for n in LINKS if "WILD Critters" in n.text)
        self.assertEqual(labels(wildlife), ("halloween-happenings", "wild-critters-and-costumes", "details"))
        trails = [n for n in LINKS if n.attrs["data-guide-item"] == "trail-7-and-the-3-dune-challenge"]
        self.assertEqual(len(trails), 2)
        self.assertEqual({n.attrs["data-guide-link"] for n in trails}, {"trail-7-route", "3-dune-challenge-route"})
        duplicates = [n for n in LINKS if strip_utm(n.attrs["href"]) == "https://friendshipbotanicgardens.org/event/haunted-trails-event-2026/"]
        self.assertEqual(len(duplicates), 2)
        self.assertEqual(len({n.attrs["data-guide-section"] for n in duplicates}), 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
