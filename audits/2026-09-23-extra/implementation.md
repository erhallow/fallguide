# Approved extra-review changes

Implemented locally on September 23, 2026, after approval of the [extra link review](./report.md). The original audit remains a pre-edit research snapshot of commit `fab6ad0`; its occurrence IDs refer to [that inventory](./inventory.json), not the revised page's link order.

## What changed

- Applied individually authored edits to 80 audit entries, including 27 primary-link replacements and seven added detail links. The page now has 190 anchor occurrences: 183 outbound web links, six internal links and one phone link, covering 163 unique web destinations.
- Replaced indirect or unusable destinations with the reviewed event, municipal, venue, booking or seasonal announcement pages. Important examples include Pumpkin Glow, Munster's hayride event, Westville Pumpkin Festival, Fair Oaks Halloween Trail, Hobart's Halloween event, St. John Boo Bash, Barker Mansion's October 24 session, Life Care Center, USW 6787, several trunk-or-treat events, Coffee Creek and Gabis.
- Corrected Pumpkin Smash Bash's extra activity charge, WILD Critters & Costumes' 4:30 p.m. closing versus 3:30 p.m. last vehicle admission, Cowles Bog's approximately four-hour outing, Gabis garden viewing versus model-train hours, and Nightfall Tour's unannounced boarding location. Added reviewed planning details such as Garwood's family U-pick minimum and Sparta Dome admission.
- Clearly identified community-calendar sources, Facebook destinations, PDF flyers and vendor-oriented pages. Where source details conflict, the card now identifies the specific uncertainty instead of presenting an unsupported time, price or location as confirmed.
- Rebuilt town trick-or-treat hours around verified 2026 information. Knox is visible with its reviewed October 31, 5:30–7 p.m. hours. The other 30 towns are in a closed-by-default, keyboard-operable disclosure, each labeled “2026 not verified.” Removed all 2025 hours and the misleading historical-window statistic. La Porte's inaccessible link was removed; its town entry remains with an explicit source-unavailable note. Westville retains the phone fallback.
- Removed Spook Fest from the dated event list because the review did not establish a reliable, accessible event source. This does **not** mean the event is canceled. The original listing and old town-hours content remain recoverable from Git and the original audit.
- Changed “Read a recent issue” to “Read a sample issue.” Preserved the two signup placeholders, the decorative checklist with four crossed-off reminders, and the footer. No printable-guide offer, functional checklist, signup backend or analytics was added.

## Deliberately unresolved

Organizer confirmation is still needed for the uncertainties called out on the page, including Whiting's hayride dates, Hebron Haunted House visitor details, St. John Boo Bash eligibility, Griffith craft-festival hours, Nightfall Tour boarding, several attraction schedules and most town Halloween hours. Retaining an explicitly unconfirmed item is not a claim that its 2026 schedule has been verified.

The stronger alternatives found in the audit were used; a more direct URL was not substituted when it had a wrong year, conflicting information, a certificate warning or no usable event content. No security warnings were bypassed.

## Verification

The checked visitor flow is: open the static guide → navigate to the Halloween section → read the confirmed hours → open and close the remaining-town list → read the mobile newsletter offer and revised source notes. External destinations were researched in the approved audit; this implementation check did not repeat all 159 original unique-destination reviews.

- `python3 scripts/check-guide.py`: **12 checks passed**, including corrected destinations and copy, current-year town statuses, internal targets, external-link protections, structured data, placeholders, footer and static reminders.
- `git diff --check`: passed.
- Existing local preview at `http://127.0.0.1:8765/`: updated content verified.
- Desktop at 1280 pixels and mobile at 390 × 844: readable layout, no horizontal document overflow or overflowing HTML content, no blocking overlays.
- Click navigation to `#p3`: passed. Town disclosure: click to open and Enter to close passed; all 30 pending towns present, no historical 2025 hours.
- Browser warning/error log: empty during verification.
- Browser-verification skills guided the desktop/mobile, console and interaction checks. The prescribed browser CLI was unavailable, so the in-app browser was used. Temporary viewport settings were reset and the verification tab was closed; the user's preview server was left running.

## Files and delivery status

Site changes are in `index.html`; regression checks are in `scripts/check-guide.py`. The [authored edit plan](./approved-edits.json) documents the per-item decisions. `scripts/prepare-approved-link-edits.py` is the one-time patch generator used for this batch; it expects the original audit baseline and is not an ongoing migration command.

At the initial implementation handoff, no commit, push or deployment had been performed.

## September 24 follow-up and release preparation

- Increased the main-page brand mark from 52 to 62 pixels high on desktop and from 38 to 42 pixels on mobile. Later section branding remains unchanged. Browser checks at 1280, 768, 390 and 320 pixels confirmed the responsive sizes and no document overflow; no browser warnings or errors were recorded.
- Replaced the “Before you go” notice with the user's exact approved wording, including the daily-review commitment. This is a copy change; it does not configure an automated daily review.
- The user authorized pushing all approved changes to `main`. Pre-push checks passed: 12 regression tests, `git diff --check`, and a check that GitHub's `main` still matched the original baseline.
- Authored reports, inventory, review decisions, edit plan and helper scripts are included. Downloaded third-party page text and PDFs (`evidence/` and `retrievals.json`, approximately 25 MB combined) remain local and are excluded by `.gitignore`. The evidence-inspection helper requires that local cache; the reports themselves link to public sources.
- The final task response records the push result and commit. No separate manual deployment is part of this release procedure.
