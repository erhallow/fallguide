#!/usr/bin/env python3
"""Read-only regression checks for the approved static fall-guide edits."""

from collections import Counter
from html.parser import HTMLParser
import json
from pathlib import Path
import unittest
from tag_links import strip_utm


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
        return [strip_utm(n.attrs["href"]) for n in node.descendants() if n.tag == "a"]

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
            for key in ("aria-labelledby", "aria-describedby"):
                for value in node.attrs.get(key, "").split():
                    self.assertIn(value, ids)

    def test_newsletter_forms_are_accessible_and_have_approved_copy(self):
        forms = [n for n in DOC.nodes if n.tag == "form"]
        self.assertEqual(len(forms), 2)
        self.assertEqual({n.attrs["data-subscribe-form"] for n in forms}, {"top", "bottom"})
        for form in forms:
            self.assertEqual(form.attrs["action"], "/api/subscribe")
            self.assertEqual(form.attrs["method"], "post")
            self.assertIn("novalidate", form.attrs)
            self.assertFalse(any(n.tag == "a" for n in form.parent.descendants()))
            self.assertNotIn("Free local news, twice a week.", form.parent.text)
            self.assertNotIn("local preview", form.parent.text)
            self.assertNotIn("Read a sample issue", form.parent.text)
            self.assertIn("Not subscribed yet? Get the best of NWI, all year long.", form.parent.text)
            self.assertIn("A local newsletter delivered to your inbox every Monday and Thursday", form.parent.text)
            email = next(n for n in form.descendants() if n.attrs.get("name") == "email")
            self.assertEqual(email.attrs["type"], "email")
            self.assertIn("required", email.attrs)
            self.assertEqual(email.attrs["autocomplete"], "email")
            self.assertTrue(any(n.tag == "label" and n.attrs.get("for") == email.attrs["id"] for n in form.descendants()))
            self.assertTrue(any(n.attrs.get("role") == "status" for n in form.descendants()))
            self.assertTrue(any(n.tag == "button" and n.text == "Subscribe for free" for n in form.descendants()))
        self.assertNotIn("Signup form goes here", HTML)
        button_style = HTML.split(".subscribe-fields button{", 1)[1].split("}", 1)[0]
        self.assertIn("background:var(--olive)", button_style)
        self.assertIn("color:#fff", button_style)
        self.assertNotIn("beehiiv_api", HTML)
        self.assertNotIn("beehiiv_pub_id", HTML)
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
        self.assertTrue({"44", "47", "66", "94"}.isdisjoint(present))

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

    def test_historical_town_hours_are_separate_from_confirmed_2026(self):
        town_section = self.by_id("town-hours")
        tiles = [n for n in town_section.descendants() if n.has_class("tile")]
        self.assertEqual(len(tiles), 30)
        self.assertFalse(any(n.has_class("slots") or n.has_class("sky") for n in town_section.descendants()))
        self.assertIn("We will be updating trick or treat times two times a week until Halloween. Check back for confirmation here. 2025 times have been included for reference.", town_section.text)
        heading = self.by_id("historical-town-hours")
        self.assertEqual(heading.tag, "h3")
        self.assertEqual(heading.text, "2025 Halloween times (reference only!)")
        self.assertTrue(heading.parent.has_class("historical-towns"))
        self.assertIn("not confirmed 2026 schedules", heading.parent.text)
        self.assertFalse(any(n.tag == "details" for n in town_section.descendants()))
        historical = {
            "2025: 5–7 p.m.": {"Cedar Lake", "Crown Point", "Griffith", "Hammond", "Highland", "Hobart", "Kouts", "La Porte", "Lowell", "Michigan City", "Munster", "Schererville", "Westville", "Whiting", "Winfield"},
            "2025: 5:30–7:30 p.m.": {"Chesterton", "Hebron", "Merrillville", "Portage", "Porter", "Valparaiso"},
            "2025: 4–7 p.m.": {"Dyer", "East Chicago"},
            "2025: 4–7:30 p.m.": {"Gary"},
            "2025: 5–8 p.m.": {"St. John"},
            "No 2025 reference": {"DeMotte", "Lake Station", "North Judson", "Rensselaer", "Wheatfield"},
        }
        for tile in tiles:
            self.assertIn("2026 not verified", tile.text)
            name = next(n.text for n in tile.descendants() if n.has_class("tn"))
            reference = next(n.text for n in tile.descendants() if n.has_class("th"))
            self.assertEqual(reference, next(hours for hours, towns in historical.items() if name in towns))
            if "La Porte" in tile.text:
                self.assertFalse(self.hrefs(tile))
                self.assertIn("Official source unavailable", tile.text)
            else:
                self.assertTrue(self.hrefs(tile))
        confirmed = next(n for n in town_section.descendants() if n.has_class("confirmed-town"))
        self.assertIn("Knox", confirmed.text)
        self.assertIn("5:30–7 p.m. Central Time", confirmed.text)
        self.assertIn("https://www.cityofknox.net/", self.hrefs(confirmed))
        self.assertNotIn("2025", confirmed.text)
        self.assertIn("have not been independently verified", town_section.text)
        self.assertNotIn("Only verified", town_section.text)

    def test_requested_farm_hours_and_copy(self):
        big_johns = self.listing(112)
        self.assertNotIn("Confirm 2026 schedule", big_johns.text)
        self.assertNotIn("The posted schedule does not state its year", big_johns.text)
        self.assertNotIn("Confirm 2026 hours and prices", big_johns.text)
        self.assertIn("Mon.–Sat. 9 a.m.–6 p.m.; closed Sundays", big_johns.text)
        self.assertIn("Open every day, 9 a.m.–dusk, through Oct. 31.", self.listing(118).text)
        self.assertIn("Open weekends, 9 a.m.–3 p.m.", self.listing(122).text)
        self.assertIn("Check the orchard’s Facebook page for confirmation before visiting.", self.listing(122).text)
        self.assertNotIn("2026 details not verified", self.listing(122).text)
        self.assertIn("Farm open weekends, 8 a.m.–6 p.m.; hayrides 10 a.m.–5 p.m.", self.listing(123).text)
        self.assertIn("Check the farm’s Facebook page for confirmation before visiting.", self.listing(123).text)
        self.assertNotIn("Confirm daily opening hours", self.listing(123).text)
        for listing_id in (122, 123):
            self.assertTrue(any(url.startswith("https://www.facebook.com/") for url in self.hrefs(self.listing(listing_id))))

    def test_extra_audit_direct_event_links(self):
        expected = {
            17: "https://www.harvesttymefun.com/pumpkin-glow-trail",
            19: "https://www.munster.org/eGov/apps/events/calendar.egov?view=item&id=4696",
            20: "https://westvillepumpkinfestival.com/",
            27: "https://www.cityofhobart.org/513/Halloween-in-the-Park",
            32: "https://stjohnin.recdesk.com/Community/Program/Detail?programId=589",
            36: "https://barkermansion.org/events/candlelight-tour-victorian-superstitions-at-barker-mansion/",
            50: "https://www.indianadunes.com/event/the-bizarre-bazaar-%40-porter-county-expo-center/5804/",
            51: "https://www.facebook.com/events/1653128139256628/",
            63: "https://www.portercountyexpo.org/Calendar.aspx?EID=565",
            67: "https://www.cityofhobart.org/513/Halloween-in-the-Park",
            69: "https://4.files.edl.io/1187/08/27/26/160512-4143b519-bef0-4f9a-80da-bb725b8c01a9.pdf",
            71: "https://www.facebook.com/photo?fbid=1665536428915376&set=pb.100063771044886.-2207520000",
            74: "https://stjohnin.recdesk.com/Community/Program/Detail?programId=589",
            76: "https://www.facebook.com/photo?fbid=1558062273027753&set=pb.100064719844819.-2207520000",
            80: "https://www.facebook.com/reel/1562628281480534",
            81: "https://www.townplanner.com/event/882580/",
            93: "https://firstchristianreformedchurch.churchcenter.com/registrations/events/3881373",
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
        self.assertIn("$5 entry fee", self.listing(56).text)
        self.assertIn("Saturday, Oct. 31, 9 a.m.–2 p.m.", self.listing(54).text)
        self.assertIn("Brumm’s Plaza, 2540 45th St., Highland, IN", self.listing(71).text)
        self.assertNotIn("Provisional", self.listing(71).text)
        self.assertIn("Unconfirmed attraction", self.listing(99).text)
        self.assertIn("Dates and hours need confirmation", self.listing(106).text)
        self.assertIn("October 23, 2026 session", self.listing(36).text)
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

    def test_requested_september_24_event_details(self):
        self.assertIn("Movie starts at dusk", self.listing(29).text)
        self.assertNotIn("time is not yet confirmed", self.listing(29).text)
        for detail in ("Oct. 23", "6–8 p.m. Central", "$25", "self-guided candlelight tour", "not a haunted house or ghost tour"):
            self.assertIn(detail, self.listing(36).text)
        pattis = self.listing(39)
        for detail in ("gymnastics", "Halloween craft", "costume parade", "trick-or-treating", "pizza party", "take-home pumpkin", "Girls ages 4–10; boys ages 4–8. No exceptions.", "Members: $43 per child / $40 for siblings", "Non-members: $46 per child / $43 for siblings"):
            self.assertIn(detail, pattis.text)
        self.assertIn("tel:+12198652274", self.hrefs(pattis))
        wildlife = next(n for n in DOC.nodes if n.tag == "li" and "WILD Critters & Costumes" in n.text)
        self.assertNotIn("service fee", wildlife.text)
        self.assertIn("$15 ages 2+", wildlife.text)
        for detail in ("100+", "1–7 p.m.", "$5 cash only", "over 13"):
            self.assertIn(detail, self.listing(50).text)
        self.assertIn("Saturday, Sept. 26, 10 a.m.–5 p.m.; Sunday, Sept. 27, 10 a.m.–4 p.m.", self.listing(51).text)
        self.assertNotIn("remain unresolved", self.listing(51).text)
        self.assertIn("double check the hours before attending - not yet included", self.listing(57).text)
        self.assertNotIn("shopper admission not yet verified", self.listing(57).text)
        expected = {
            48: ("10 a.m.–4 p.m.", "545 E. 110th Ave., Crown Point"),
            53: ("Oct. 17", "9 a.m.–3 p.m.", "Westville Elementary School"),
            56: ("Oct. 24", "10 a.m.–4 p.m.", "$5 entry fee", "Sparta Dome"),
            54: ("Friday, Oct. 30, 5–9 p.m.", "Saturday, Oct. 31, 9 a.m.–2 p.m.", "$5 at the door"),
            59: ("Nov. 7", "9 a.m.–2 p.m.", "3401 N. Valparaiso St., Valparaiso, IN"),
            61: ("2–7 p.m.", "YMCA Camp Triangle Hills Lodge"),
        }
        for listing_id, details in expected.items():
            for detail in details:
                with self.subTest(listing=listing_id, detail=detail):
                    self.assertIn(detail, self.listing(listing_id).text)

    def test_requested_community_trick_or_treat_updates(self):
        community = next(n for n in DOC.nodes if n.tag == "section" and n.attrs.get("aria-labelledby") == "tr-h")
        listings = [n for n in community.descendants() if n.tag == "li"]
        self.assertEqual(len(listings), 29)
        stat = next(n for n in DOC.nodes if n.tag == "dt" and n.text == "Community treats")
        self.assertEqual(next(n.text for n in stat.parent.children if n.tag == "dd"), "29")
        self.assertNotIn("Life Care Center", DOC.root.text)
        self.assertNotIn('data-audit-id="66"', HTML)
        expected = {
            68: ("Oct. 10", "3–7 p.m.", "3641 S. Randolph St., Hobart, IN"),
            70: ("Oct. 16", "Friday, 5–7 p.m.", "Southlake YMCA"),
            71: ("Oct. 17", "2–4 p.m.", "Brumm’s Plaza, 2540 45th St., Highland, IN", "Facebook photo"),
            72: ("Oct. 17", "10 a.m.–noon", "228 E. Lincolnway, La Porte"),
            73: ("Oct. 17", "5–8 p.m.", "Faith Fellowship Church"),
            76: ("Oct. 18", "4–6 p.m.", "American Legion Post 260", "Facebook photo"),
            80: ("Oct. 23", "Friday, 4–6:30 p.m.", "1121 Merrillville Rd., Crown Point, IN", "Facebook reel"),
            81: ("Oct. 23", "6–8 p.m.", "225 W. 77th Ave."),
            82: ("Oct. 23", "Starts 6:30 p.m.", "2510 Monroe St., La Porte"),
            86: ("Oct. 24", "Starts 4:30 p.m.", "270 County Road 325 E., Valparaiso, IN"),
            87: ("Oct. 24", "5–7 p.m.", "100 Millpond Rd., Union Mills, IN"),
            89: ("Oct. 25", "Starts 2 p.m.", "745 E. 43rd Ave., Gary"),
            90: ("Oct. 28", "5:30–7:30 p.m.", "5281 Fountain Dr., Suite B, Crown Point, IN"),
            92: ("Oct. 29", "Starts 5 p.m.", "501 Allen Court, Chesterton"),
            93: ("Oct. 30", "6–9 p.m.", "Crown Point Christian Reformed Church parking lot", "trunk hosts and volunteers"),
        }
        for listing_id, details in expected.items():
            for detail in details:
                with self.subTest(listing=listing_id, detail=detail):
                    self.assertIn(detail, self.listing(listing_id).text)
        self.assertNotIn("9717 Spring St.", self.listing(71).text)
        self.assertNotIn("270 Rigg Rd.", self.listing(86).text)
        self.assertNotIn("automatic map", self.listing(87).text)
        self.assertNotIn("6–8 p.m.", self.listing(93).text)
        note = next(n.text for n in community.children if n.has_class("fine"))
        self.assertEqual(note, "Check the event link before you go to confirm details! Event details may change and are at the discretion of the event organizers.")

    def test_fall_graphic_dates_and_removed_notes(self):
        self.assertNotIn("Illustrative trend, rounded to 5 minutes.", DOC.root.text)
        self.assertNotIn("Check exact local sunset times", DOC.root.text)
        self.assertNotIn("Color varies by tree species, weather and location.", DOC.root.text)
        label = self.by_id("vine").attrs["aria-label"]
        self.assertIn("approximate weekly dates from September 21 through November 30", label)
        self.assertIn('var weeks=[["Sept.","21",0],["","28",0],["Oct.","5",1]', HTML)
        self.assertIn('["","19",3],["","26",3],["Nov.","2",4]', HTML)
        self.assertIn(">approximate dates</text>", HTML)
        self.assertNotIn("approximate dates · just for fun", HTML)

    def test_no_unverified_event_schema(self):
        schemas = [json.loads(n.text) for n in DOC.nodes if n.attrs.get("type") == "application/ld+json"]
        self.assertEqual(len(schemas), 1)
        self.assertEqual(schemas[0]["@type"], "CollectionPage")
        self.assertNotIn('"@type": "Event"', HTML)
        self.assertEqual(schemas[0]["url"], "https://fallguide.nwiexplored.com/")

    def test_before_you_go_callout_preserves_copy_and_emphasizes_action(self):
        heading = self.by_id("before-you-go-heading")
        self.assertEqual(heading.tag, "h2")
        self.assertEqual(heading.text, "Before you go:")
        notice = heading.parent.parent
        self.assertEqual(notice.tag, "aside")
        self.assertEqual(notice.attrs["role"], "note")
        self.assertEqual(notice.attrs["aria-labelledby"], heading.attrs["id"])
        self.assertEqual(" ".join(notice.text.split()), "Before you go: We've spent countless hours putting this guide together, but event details can change. Before you head out, please double-check the original listing linked with each event. We'll be reviewing and updating this guide daily all season long.")
        emphasis = [n.text for n in notice.descendants() if n.tag == "strong"]
        self.assertEqual(emphasis, ["Before you head out, please double-check the original listing linked with each event."])

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
