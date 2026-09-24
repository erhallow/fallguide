# Approved updates — implementation record

Implemented locally on September 23, 2026, following approval of the 11 sections in [copy-edits.md](./copy-edits.md). That document and the [original link audit](./link-audit.md) remain the pre-change review record, not a description of the revised page. The website has not been committed, pushed, or deployed by this update.

## What changed

| Approval | Implementation |
| --- | --- |
| 1. Writing standards | More consistent dates, times, town names, price/age labels, source notes and confirmation caveats. Duplicate listings were reconciled during this edit; they are still static HTML, not a shared-data system. |
| 2. Opening and navigation | Clearer local introduction, prominent newsletter connection, section navigation, and a shorter before-you-go notice. Removed unsupported precise foliage forecasts; retained an explicitly illustrative fall-color graphic. Sunset times are approximate, rounded to five minutes, and linked to a local reference. |
| 3. Newsletter | Both form placeholders remain, as requested. Revised the offer to the free Monday/Thursday newsletter, moved the first placeholder near the top, and added a recent-issue link. Removed printable-guide promises. No form submission, email collection, or delivery flow was installed or tested. |
| 4. Events and markets | Corrected mismatched destinations, clarified descriptions and admission terms, fixed supported date discrepancies, and ordered concerts/markets chronologically. Held two unsupported listings rather than linking them to unrelated events. |
| 5. Community trick-or-treating | Clearer names, venues, times and year caveats. Moved the adult downtown outing to grown-up parties and removed its family-list duplicate; 30 community entries remain. Added the official WILD Critters & Costumes link. |
| 6. Haunts | Reviewed and revised all 14 cards; replaced unsourced scare scores with experience descriptions. Corrected Skarva Manor's format and Woodland Park's confirmed dates, and kept unresolved schedules explicitly qualified. |
| 7. Town hours | Separated confirmed 2026 information from 2025 references. Added a municipality contact/source link to all 31 town tiles. Added newly verified Knox hours above the historical chart. |
| 8. Farms and orchards | Revised all 17 cards, including 2026 crop restrictions, seasonal opening details, pricing caveats and specific destinations. Apple Blossom's lack of 2026 apple picking is prominent. |
| 9. Hikes | Revised all 13 cards; corrected route lengths, difficulty and access descriptions. Trail 7 and the 3 Dune Challenge now have separate, clearly labeled route links. |
| 10. To-do list | Kept 12 simple reminders. Four have decorative checks and strikethrough: clean gutters, book a furnace tune-up, swap clothes, and buy costumes. No inputs, toggle behavior, storage, due dates or progress tracking. |
| 11. Footer | Added publisher identity, review date, planning caveat, newsletter and recent-issue links, back-to-top navigation, and copyright. |

Also added one main landmark, a keyboard-focusable skip-link target, a single top-level heading, visible link focus styles and accessible chart descriptions. Adjusted mobile spacing, card typography, grids and date badges while preserving the seasonal illustrations and visual style.

The large deletion in the HTML diff is primarily the removal of 88 unreliable `Event` structured-data records. A `CollectionPage` record remains. Unverified dates, admissions and venues are no longer represented to search engines as confirmed event facts.

## Important link corrections and held entries

Original audit IDs are retained in `data-audit-id` attributes so changes can be traced.

- **023:** Fair Oaks Halloween Trail now points to Fair Oaks' harvest-season page.
- **041–043, 045–046:** Repaired shifted links for Sarah's Place, the VU Symphony, Journeyman's Halloween Party, Without U2 and Halloween Bash '26 NWI.
- **033 and 102:** Both Friendship Gardens appearances now link to the official 2026 Haunted Trails event.
- **044 Hellbilly Deluxe and 047 Rocky Horror:** Removed from the visible guide pending a matching, dated local event announcement. Original details remain recoverable in the audit and Git history.
- **094:** Removed only the duplicate adult outing from the family/community list; listing 040 remains in the appropriate section.
- **130:** The combined hiking card no longer sends readers of both routes to a Trail 7-only article.

## New confirmation and remaining editorial work

[Knox's official city calendar](https://www.cityofknox.net/) lists Halloween trick-or-treating on October 31, 2026, from **5:30–7 p.m. Central Time**. This was checked during implementation on September 23. It replaces the inaccurate blanket suggestion that no town has posted 2026 hours.

The other 30 towns' current-year hours have **not** been verified in this guide. Existing historical windows remain explicitly labeled and have not been independently certified. Municipal websites are starting points for checking current announcements, not citations proving the historical hours. Westville uses the town hall's published telephone contact because its website had a certificate problem; no security warning was bypassed.

Some organizer sources still omit a year, require login, offer only vendor information, or disagree with themselves. Their listings retain specific caveats; “source reviewed” must not be interpreted as “every detail confirmed.” The original link inventory documents those limitations. The Hometown Hocus Pocus year/opening-time conflict, unconfirmed shopper admission at some markets, and several social-media-only events still need organizer confirmation.

Privacy and corrections links were not invented. Add the publisher's real privacy destination and monitored corrections channel when supplied, along with the live signup integration in a later approved change. No printable version is planned or promised.

## Verification

- `python3 scripts/check-guide.py`: **8 tests passed**. Covers corrected link mappings, 44-card preservation, all internal anchors/SVG references, unique IDs, placeholders, 12 static reminders/four completed items, separate town-year labels, footer and structured data.
- Inline application JavaScript passed `node --check`.
- `git diff --check` passed.
- Browser checks at **320 px, 390 px and 1280 px** found no horizontal page overflow. Inspected the hero/signup, event layout, haunt cards, checklist, town-hours section and footer.
- Section-link navigation works. The skip link moves keyboard focus to the main content. Clicking a reminder does not change the four completed items.
- Both generated charts render. No browser console warnings or errors were recorded during the checks.
- Static local preview only: no backend, database, signup submission or production deployment was exercised. External link meaning was reviewed using the editorial audit and current primary sources; the regression script itself does not test remote availability.

Local preview: [http://127.0.0.1:8765/](http://127.0.0.1:8765/) while the preview server is running.
