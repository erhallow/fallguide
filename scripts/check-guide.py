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
            23: "https://fofarms.com/halloween-trail/",
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
        self.assertEqual(notes, ["2026 date and time verified from organizer event page. · Facebook event"])
        self.assertNotIn("A dated event announcement is needed", listing.text)
        self.assertNotIn("2026 details not verified", listing.text)

    def test_only_verified_current_town_hours_are_shown(self):
        town_section = self.by_id("town-hours")
        tiles = [n for n in town_section.descendants() if n.has_class("tile")]
        self.assertEqual(len(tiles), 30)
        self.assertNotIn("2025", town_section.text)
        self.assertFalse(any(n.has_class("slots") or n.has_class("sky") for n in town_section.descendants()))
        pending = next(n for n in town_section.descendants() if n.tag == "details")
        self.assertIn("30 schedules not yet verified", pending.text)
        for tile in tiles:
            self.assertIn("2026 not verified", tile.text)
            self.assertNotIn("p.m.", tile.text)
            if "La Porte" in tile.text:
                self.assertFalse(self.hrefs(tile))
                self.assertIn("Official source unavailable", tile.text)
            else:
                self.assertTrue(self.hrefs(tile))
        confirmed = next(n for n in town_section.descendants() if n.has_class("confirmed-town"))
        self.assertIn("Knox", confirmed.text)
        self.assertIn("5:30–7 p.m. Central Time", confirmed.text)
        self.assertIn("https://www.cityofknox.net/", self.hrefs(confirmed))

    def test_extra_audit_direct_event_links(self):
        expected = {
            17: "https://www.harvesttymefun.com/pumpkin-glow-trail",
            19: "https://www.munster.org/eGov/apps/events/calendar.egov?view=item&id=4696",
            20: "https://westvillepumpkinfestival.com/",
            27: "https://www.cityofhobart.org/513/Halloween-in-the-Park",
            32: "https://stjohnin.recdesk.com/Community/Program/Detail?programId=589",
            36: "https://barkermansion.org/events/candlelight-tour-victorian-superstitions-at-barker-mansion-2/",
            50: "https://www.townplanner.com/boone-grove/in/event/arts-and-entertainment/the-bizarre-bazaar-at-the-porter-county-expo-center/20260926/877285/",
            51: "https://www.facebook.com/events/1653128139256628/",
            63: "https://www.portercountyexpo.org/Calendar.aspx?EID=565",
            66: "https://www.portagein.gov/Calendar.aspx?EID=3012&month=10&year=2026&day=8&calType=0",
            67: "https://www.cityofhobart.org/513/Halloween-in-the-Park",
            69: "https://4.files.edl.io/1187/08/27/26/160512-4143b519-bef0-4f9a-80da-bb725b8c01a9.pdf",
            71: "https://stayhappening.com/e/trunk-or-treat-E2ISYV8NP99",
            74: "https://stjohnin.recdesk.com/Community/Program/Detail?programId=589",
            76: "https://www.townplanner.com/event/883786/",
            80: "https://www.townplanner.com/event/882998/",
            81: "https://www.townplanner.com/event/882580/",
            93: "https://www.townplanner.com/event/883796/",
            101: "https://www.chaostrips.com/book-online",
            114: "https://www.scheeringafarm.com/fall-fun",
            121: "https://pavolkafruitfarm.com/picked-%26-u-pick",
            131: "https://coffeecreekpreserve.org/trail-map-guidelines/",
            132: "https://www.pnw.edu/gabis-arboretum/plan-your-visit/",
        }
        for listing_id, url in expected.items():
            with self.subTest(listing=listing_id):
                self.assertEqual(self.hrefs(self.listing(listing_id))[0], url)
        self.assertNotIn("Spook-Fest", DOC.root.text)
        self.assertNotIn("https://www.townplanner.com/event/882073/", HTML)
        self.assertNotIn("https://www.cityoflaporte.com/departments/government", HTML)

    def test_extra_audit_copy_corrections(self):
        self.assertIn("Pumpkin smashing costs extra", self.listing(24).text)
        self.assertNotIn("Included with orchard admission", self.listing(24).text)
        wildlife = next(n for n in DOC.nodes if n.tag == "li" and "WILD Critters & Costumes" in n.text)
        self.assertIn("10 a.m.–4:30 p.m.", wildlife.text)
        self.assertIn("last vehicle admission 3:30 p.m.", wildlife.text)
        self.assertIn("around 4 hours", self.listing(127).text)
        self.assertIn("model trains run", self.listing(132).text)
        self.assertIn("Garden viewing daily", self.listing(132).text)
        self.assertIn("Boarding location is to be announced", self.listing(100).text)
        self.assertNotIn("Hammond departure", self.listing(100).text)
        self.assertIn("$20 U-pick purchase per family", self.listing(117).text)
        self.assertIn("$5 shopper admission", self.listing(56).text)
        self.assertIn("Saturday opening time conflicts", self.listing(54).text)
        self.assertIn("Provisional", self.listing(71).text)
        self.assertIn("Unconfirmed attraction", self.listing(99).text)
        self.assertIn("Dates and hours need confirmation", self.listing(106).text)
        self.assertIn("October 24 session only", self.listing(36).text)
        for listing_id in (109, 115, 121):
            self.assertNotIn("daily 9 a.m.–5 p.m.", self.listing(listing_id).text)

    def test_external_links_and_new_detail_links(self):
        for n in DOC.nodes:
            if n.tag == "a" and n.attrs.get("target") == "_blank":
                self.assertIn("noopener", n.attrs.get("rel", "").split())
        for listing_id in (95, 104, 110, 117, 126):
            self.assertEqual(len(self.hrefs(self.listing(listing_id))), 2)
        self.assertIn("PDF flyer", self.listing(69).text)
        self.assertIn("DNR access guide (PDF)", self.listing(136).text)

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
