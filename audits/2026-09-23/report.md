# Fall Guide review: accuracy, clarity, and newsletter conversion

**Reviewed September 23, 2026 · Website: [fallguide.nwiexplored.com](https://fallguide.nwiexplored.com/)**

This is a recommendations-only audit. No website copy, links, forms, or deployment settings were changed.

[Complete 138-link inventory](./link-audit.md) · [Suggested copy edits](./copy-edits.md)

## Bottom line

The seasonal visual identity, local coverage, and practical planning information give this guide a strong foundation for attracting newsletter readers. The main problem is that the guide currently **does not have a working way to subscribe**: both signup sections say “Signup form goes here.”

Before promoting it as a lead magnet, I would prioritize a working signup experience and trustworthy visit-planning information. I found **eight links pointing to unrelated content**, **two appearances of the same outdated event link**, and several meaningful conflicts in event dates, farm availability, and trail descriptions.

A beautiful, useful guide earns attention. Reliable details and a clear reason to keep receiving NWI Explored are what turn that attention into subscriptions.

## 1. Fix before the next promotional push

| Priority | Finding | Recommended action |
| --- | --- | --- |
| P0 — conversion | Both signup areas are placeholders. A printable guide is promised, but no download or delivery mechanism is present in this site. | Add and test the actual newsletter form. Only promise a printable once its delivery works. Explain that signup includes the ongoing newsletter. |
| P1 — wrong links | Eight event titles lead to unrelated destinations. | Correct the mappings below, including their copies in structured data. Hold listings without a verified source. |
| P1 — wrong season | Friendship Gardens Haunted Trails links to its 2025 event in two places. | Replace both with the official 2026 page. |
| P1 — visit-planning errors | Some market dates, farm schedules, apple-picking availability, and attraction descriptions conflict with sources. | Resolve the high-impact discrepancies below. Do not copy an internally contradictory source without confirmation. |
| P1 — historical hours | 2025 trick-or-treat hours appear alongside prominent 2026 Halloween information, with no town-by-town source links. | Separate 2026 confirmed times from historical references; label every town with its year and status. |
| P2 — trust and usability | Some listings lack times, venues, price labels, or directly relevant sources; precise foliage claims are unsourced. | Apply the copy standards and link-level recommendations in the companion documents. |

P0 and P1 describe recommended implementation order, not a claim that a security emergency exists.

### The eight unrelated destinations

These are relevance failures, not ordinary expired-link errors. The destination loads but is about something else.

| Guide item | Current destination describes | Recommended destination / disposition |
| --- | --- | --- |
| Halloween Trail at Fair Oaks | La Porte County Fair | [Fair Oaks Harvest Season](https://fofarms.com/harvest-season/) — explicitly lists the Oct. 31 Halloween Trail. |
| Acorn Concert Series: Sarah's Place | Sandy Oak Ranch wildlife events | [PNW Sarah’s Place concert](https://www.pnw.edu/event/acorn-concert-series-sarahs-place-zach-bryan-and-noah-kahan-tribute/) |
| VU Symphony Halloween Spooktacular | Sarah’s Place concert at PNW | [Valparaiso University Symphony listing](https://www.valparaisoevents.com/event/valparaisouniversitysymphonyorchestrahalloweenspooktacular) |
| Journeyman’s Halloween Party | VU Symphony concert | [Official Journeyman party page](https://www.journeyman.com/events/halloween-party-valparaiso-in-26/) |
| Hellbilly Delux Halloween Bash | Journeyman’s party | Find the dated Portage venue/ticket page. The band's Facebook profile alone does not verify this event. Correct “Delux” to “Deluxe.” |
| Without U2 Halloween Bash | Hellbilly Deluxe band profile | [Hobart Art Theater concert](https://brickartlive.com/event/without-u2-driver-8-tributes-to-u2-r-e-m/) |
| Halloween Bash ’26 NWI | Without U2 concert | [Duneland Falls Halloween Bash tickets](https://www.eventbrite.com/e/halloween-bash-26-nwi-adult-halloween-party-costume-contest-tickets-1993982098132) |
| The Rocky Horror Picture Show | Duneland Falls adult party | No matching 2026 Griffith screening was verified. Obtain an official screening source before retaining the dated listing. |

The consecutive mismatches in the concert section suggest an offset in the title-to-URL mapping, but this is a pattern observed in the output, not a proven explanation of how the page was authored.

Also add a link to **WILD Critters & Costumes**, which currently has none. Its [official event page](https://www.sorwildlife.com/event-details/wild-critters-and-costumes) lists Oct. 31, 2026, 10 a.m.–3:30 p.m.

### Other high-impact corrections

| Item | Guide currently says | Source evidence and recommendation |
| --- | --- | --- |
| Friendship Gardens Haunted Trails | Oct. 18, 2026, but links to 2025 | The [2026 page](https://friendshipbotanicgardens.org/event/haunted-trails-event-2026/) supports Oct. 18, 2–5 p.m., $4 child / $8 adult. Keep those details and update both links. |
| Hometown Hocus Pocus | Oct. 23–24; $4 / $5; Sat. 10 a.m.–4 p.m. | The [market page](https://www.yourhometownevents.com/hocuspocus/) advertises Oct. 30–31 and $5 entry. Saturday opening conflicts within the source: 9 a.m. in the schedule, 10 a.m. in the timeline; both use a 2 p.m. close. Confirm the year and Saturday opening with the organizer. |
| Spooktacular Craft & Vendor Market | Oct. 24 only, 10 a.m., Free | The [event page](https://hometownvendormarket.com/northwestindianaspooktacular/) lists Oct. 24–25, 2026: Sat. 10 a.m.–8 p.m.; Sun. noon–6 p.m. Verify shopper admission independently of vendor fees. |
| 3 Little Birds Holiday Market | Nov. 14–15 | The [2026 ticket product](https://www.3littlebirdsmarket.net/product/2026-holiday-market-admission/25) explicitly lists **Nov. 13–14**, Fri. 4–8 p.m.; Sat. 9 a.m.–4 p.m., at Porter County Expo Center. |
| Woodland Park Haunted Hayrides | Oct. 15–17 and 22–24 | The [official page body](https://portagein.gov/494/Haunted-Hayride) gives Oct. 22–24 for 2026; its description metadata still includes the other weekend. Confirm before retaining Oct. 15–17. |
| Skarva Manor | A walk-through, with a St. Jude fundraiser and Oct. 28/31 programming | The [official About page](https://www.skarvamanorhh.com/about-us) explicitly describes a **front-yard display, not a walk-through haunted house**. Current home/news information says it reopens Sept. 28, 2026. The fundraiser claims were not substantiated. Rewrite the card. |
| Apple Blossom Trails | U-pick apples; “No 2026 details yet” | Its [official homepage](https://www.appleblossomtrails.com/) says **no apple picking in 2026** because of summer weather. Remove that activity and replace the stale status. |
| Radke Orchards | Hours TBA; typically closes at 6 p.m. | Its [homepage](https://www.radkeorchards.com/) has a 2026 banner: open from Sept. 5, daily 8:30 a.m.–5:30 p.m., with a limited crop. Update hours and add the crop notice. |
| Big John’s | Sunday hours; hours not posted | Its [pumpkin page](https://bigjohnsfarmmarket.com/fall/pumpkin-patch/) now says Mon.–Sat. 9 a.m.–6 p.m., **closed Sundays**, Sept. 18–Oct. 31. The text does not explicitly identify the year; reconcile before calling it 2026-confirmed. |
| Hidden Creek | Closed Thursdays; last year’s Sept. 27 opening | Its [homepage](https://www.hcpumpkins.com/) now shows an Oct. 3 opening and Thu.–Fri. noon–4 p.m., Sat.–Sun. 11 a.m.–4 p.m. Other dates look mixed-season. Confirm which schedule applies to 2026. |
| BACA sensory-friendly event | Crown Point | [Facebook event metadata](https://www.facebook.com/events/1063118299915866/) says Schererville, despite “Crown Point Learning Center” in the title. Confirm the actual address before giving directions. |
| West Beach, Cowles Bog, Seidner | Easy / Moderate / Easy | Official sources describe [West Beach](https://www.nps.gov/indu/planyourvisit/wb16.htm) as easy to moderate with 270+ stairs, [Cowles Bog](https://www.nps.gov/indu/planyourvisit/cb16.htm) as moderate to rugged, and [Seidner’s DNR map](https://www.in.gov/dnr/nature-preserves/files/np-Seidner.pdf) as moderate, with an access walk and no parking lot. These distinctions affect suitability. |

Wickedly Whiting is another season-clarity issue: the guide's Oct. 2–3 dates align with the site's 2026 FAQ, but the linked homepage prominently displays the 2025 edition. Prefer a clear current-year announcement after resolving the FAQ's year typo.

## 2. Make historical and uncertain information unmistakable

The opening notice says older information is marked everywhere. It is not consistent: Elzinga's farm card is marked as previous-season information while its haunt card says “Open now.”

The Halloween section is especially easy to misread. It combines “Sat Oct 31,” a 2026 sunset time, and “Most towns 5 to 7 pm” with historical town hours. The current data contains 26 known historical time windows plus five unknown entries. Fifteen of those 26 known windows are 5–7 p.m.; that is not a basis for an unqualified current-year claim about all towns.

Recommended structure:

- **2026 confirmed hours:** only entries with dated current-year town sources.
- **2025 reference only:** a collapsed historical list, clearly labeled on every town.
- **2026 hours not yet verified here:** use this when no current source has been checked. Avoid “No NWI town has posted,” which requires a region-wide current check.
- For each town: official source link, year, date checked, and any residency or participation restrictions.
- Replace “Not posted” with “2026 not verified” or “No historical reference,” depending on what the field actually means.

Do not blend a 2021 DeMotte reference into a 2025 table. Historical hours are a useful preview, not instructions for Halloween 2026.

Similarly, reserve “2026 dates confirmed” for dated evidence, and record prices separately. A confirmed opening date does not confirm every attraction, crop, ticket price, or age rule.

## 3. Make the guide work as a newsletter lead magnet

### Offer a clear ongoing benefit

“Get the October update” is timely but undersells why someone should remain subscribed after Halloween. The main [NWI Explored newsletter](https://nwiexplored.com/) currently describes a free Monday-and-Thursday schedule. Connect this guide to that ongoing value.

Suggested starting version:

> **Keep your fall plans up to date**
>
> Get local events and fall updates from NWI Explored, delivered free every Monday and Thursday.
>
> **Join for free**

Once the printable is real and tested:

> **Get the printable fall guide**
>
> Get the guide plus NWI Explored’s free Monday-and-Thursday newsletter, with local events and seasonal updates.
>
> **Email me the guide**

Do not promise updates “the day they land” unless you intend to run a separate immediate-alert workflow. Use “We’ll include confirmed Halloween hours as they’re added” if that accurately describes the planned newsletter process.

### Put signup where readers will see it

In the 390 × 844 mobile browser check, the first signup block began about **3,185 pixels down**, nearly four screen heights from the top. On the 1280 × 720 desktop view, it began around 1,790 pixels down. This is a layout observation, not measured abandonment data.

Recommended placement:

1. A compact email signup near the opening value proposition.
2. A contextual signup beside the town-hours section.
3. The existing bottom signup after the full guide.

Keep the useful guide public so people can search, share, and evaluate it. Offer the printable and continuing updates as the reason to subscribe. Avoid an immediate full-screen gate before readers see any local value.

Use one required field, email, initially. If town interests would improve the newsletter, ask optionally after signup. Add a privacy link, a clear ongoing-newsletter explanation, and visible success/error states. Link the brand to the main newsletter and provide a sample issue.

### Improve the reading order

The sunset chart and checklist have personality, but visitors looking for this weekend's plans or trick-or-treat hours must scroll past them first.

Recommended order:

1. Guide title, local benefit, and signup.
2. Jump links to events, Halloween hours, farms, and hikes.
3. A small set of verified upcoming picks.
4. The comprehensive listings.
5. Seasonal background, checklist, and source/update notes.

This is a conversion hypothesis to test, not a measured guarantee. Keep the current warm visual identity.

### Measure subscriptions, not just page views

Track the guide as a distinct acquisition source, for example “fallguide-2026.” Measure confirmed new subscribers relative to unique guide visitors, and instrument form views, submissions, confirmations, and printable delivery. Preserve attribution if signup crosses from the subdomain to a newsletter platform.

Follow with subscriber engagement and unsubscribes to see whether the guide attracts the right audience. Establish a baseline before setting targets; no conversion benchmark was measured here.

No client-side analytics integration was evident in the inspected HTML, but that does not rule out server-side or platform analytics.

## 4. Other editorial, usability, and technical recommendations

### Clarity and organization

- Rename “Trunk-or-treats” to “Community trick-or-treating.” The 31 entries include a downtown Pumpkin Walk, other formats, and a 21+ shopping event. Move that adult event to the grown-up section and update counts.
- Add hours when the source provides them. The sentence “Listings without a time only posted a date” is inaccurate; several linked pages do supply times.
- Use the same order for each listing: date, time, venue/town, cost, age/access rules, one short description, source/status.
- Replace unlabeled prices such as “$15 / $20” with “$15 advance / $20 day of show.”
- Explain that times are Central Time, and distinguish market hours from attraction hours.
- Use “estimated scare level” only with a disclosed basis. Do not imply that all haunts were personally tested, or that a ghost rating guarantees age suitability.
- Avoid exact foliage dates and “three days late” without a dated forecast source. “Typical fall-color window; timing varies” is more credible.
- The sunset chart's clock-time shift includes the one-hour clock change. “Evening light lost” can be mistaken for physical daylight loss; relabel it accordingly.

The [copy-edit document](./copy-edits.md) contains specific replacement wording, including every full haunt, farm, and hike card.

### Browser observations

The guide loaded at desktop and mobile sizes, with no horizontal overflow observed at 390 pixels. The checklist persisted a test checkmark after reload; that test state was then cleared. Internal section targets exist; navigation to the events and Halloween sections was exercised successfully.

The desktop haunt grid is dense at five columns, with small body text. Consider three columns at that width and larger text for dates, fees, and warnings. The mobile page is very long—about 26,090 pixels in the checked state—so persistent or repeated section navigation would help.

The sunset chart has an accessible summary, but its individual date interaction is pointer/touch-oriented. Provide equivalent keyboard access or a text table. The page has four h1 headings and no main landmark; simplify it to one page heading with section headings and add a main landmark/skip link. This is an accessibility/structure recommendation, not a claim of an automatic SEO penalty.

### Structured data

The HTML contains 88 Event records. Some repeat the visible link mismatches and stale dates. At least three location fields contain descriptive copy instead of a place: Crown Point Oktoberfest uses its activity list as the locality, Sarah's Place uses “kids 12 & under free,” and Pumpkin Glow uses “nighttime lights trail.”

Recurring dates also need attention: Pumpkin Glow and Johnson's Pumpkin Festival have only their opening date as both start and end in their records, while the four-session candlelight tour is represented as a continuous Oct. 23–30 span.

Use a shared event data source for visible cards, repeated listings, and structured data. Store the venue, city, dates, price, source URL, and verification status explicitly instead of extracting them from display strings.

Google's [Event structured-data guidance](https://developers.google.com/search/docs/appearance/structured-data/event) expects a unique page focused on an individual event for its event experience. Do not assume an aggregate guide with 88 Event objects is eligible for 88 event rich results. Correct the underlying data first; consider individual event pages only if they serve readers and can be maintained.

## 5. Recommended follow-up checks — not performed in this audit

| Review | What to verify |
| --- | --- |
| Signup and delivery | Test a real approved email through submit, confirmation, welcome message, guide delivery, and unsubscribe. Check duplicate signup, invalid email, error states, and mobile embedding. No signup was submitted in this audit. |
| Current event facts | Resolve all “confirm” items, dated social sources, and source conflicts. Review cancellation/closure claims. Town-by-town 2026 hours need a separate official-source pass. |
| Accessibility | Keyboard-only navigation, visible focus, contrast measurements, 200% zoom, 320-pixel layout, screen-reader output, form errors, and realistic touch targets. This was not a formal WCAG audit. |
| Mobile devices | Safari/iPhone and Chrome/Android, including the actual signup embed. Only browser viewport checks were completed. |
| Performance | Lighthouse and field Core Web Vitals after the real form/tracking are installed. No performance score was measured here. |
| Printable | Letter/A4 page breaks, legible type, clickable links, QR/short site link, current year/date, and correct historical labels. “Page 1 of 4” currently describes web sections, not a verified four-page print layout. |
| Search and sharing | Rich Results Test, indexing/canonical checks, current title/description, social-preview rendering, and consistency between visible content and metadata. |
| Maintenance | Weekly source review during the season; a tighter check before major event weekends and Halloween. This is a recommendation only—no automation was created. |

## Scope and evidence limits

Reviewed the live page's visible text, rendered checklist, four sections, all 44 full cards (14 haunts, 17 farms, 13 hikes), event/market lists, and 31 town tiles. Inventoried every anchor and attempted all 125 unique external destinations. Inspected external destination content, with browser and official-source follow-ups for relevant blocked or dynamic pages, and visually reviewed both linked DNR maps.

The local and downloaded live HTML matched exactly at the audit snapshot. The audit distinguishes destination relevance from fact verification: **67 links classified “Match” still have notes when individual claims need confirmation.** Twenty-six links had limited public verification, nine offered weak support, and one Facebook event could not be meaningfully verified without login. These are not automatically broken links.

This review is current to September 23, 2026. Source pages can change. No purchases, registrations, private-account access, organizer outreach, production edits, commits, pushes, or deployments were performed.

