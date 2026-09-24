# Fall guide link tracking

Implemented locally September 24, 2026. Nothing in this change enables a paid plan,
changes Vercel account settings, commits, pushes, or deploys the website.

## What is labeled

All 181 outgoing HTTP(S) links have static UTM parameters, so they work even without
JavaScript. This includes event titles, supplemental ticket/map/source links,
farms, trails, town websites, newsletter links, and header/footer links.
Internal navigation, telephone links, SVG references, assets and SEO URLs are unchanged.

| Parameter | Value |
| --- | --- |
| `utm_source` | `nwi_explored` |
| `utm_medium` | `referral` |
| `utm_campaign` | `fall_guide_2026` |
| `utm_content` | `section__item__link` |

Example: `harvest-festivals-and-fall-outings__pumpkin-smash-bash__details`.
Section and item names are lowercase hyphenated labels. The final part identifies
the particular link: `details`, `hours-and-admission`, `preserve-map-pdf`, etc.
The same destination in two sections has different labels. The 2025 reference
town hours and confirmed 2026 town hours are labeled separately.

Existing destination query parameters and fragments are preserved. No incoming
visitor parameters, email addresses, or contact identifiers are copied to these links.
Some destinations or redirects may ignore or remove UTMs; the guide's own click
event is independent of whether the destination understands UTMs.

## UTMs versus your click reports

UTMs describe referrals in the **destination website's analytics**. Adding them to
outgoing links does not by itself give NWI Explored a report of clicks, and outgoing
UTMs do not appear as incoming traffic in the guide's Vercel UTM report.

For your own reports, `scripts/link-analytics.js` prepares a Vercel custom event:

- Event: `guide_link_click`
- `section`: e.g. `harvest-festivals-and-fall-outings`
- `item`: e.g. `pumpkin-smash-bash__details`

The link variant is included in `item` to fit base Pro's two-property limit.
Filter by section to compare events in one section, or inspect item values to see
which event and which specific link was clicked. These are click counts, not
confirmed visits, purchases, newsletter subscriptions, or unique people.

Left-click, keyboard activation, modifier-click and middle-click are supported.
Right-click menus, copied links, blocked JavaScript, and analytics blockers can
prevent measurement. Navigation never waits for tracking. Telephone and internal
navigation clicks are intentionally excluded from this outbound report.

## Vercel activation still needs verification

The live guide is hosted by Vercel, but on September 24 the public
`/_vercel/insights/script.js` endpoint returned HTTP 404. The connected Vercel tool
listed a different project (`nwi-ultimate`), so the guide's Analytics status and
plan could not be verified. No unrelated project was changed.

Before publishing this integration:

1. Open the Vercel project that owns `fallguide.nwiexplored.com`.
2. Confirm Web Analytics is enabled in that project's Analytics tab.
3. Confirm the plan supports custom events. As documented on September 24, 2026,
   custom events require **Pro or Enterprise**; Hobby supports page views but not
   these event/item click reports. Do not upgrade without the owner's approval.
4. Deploy the approved local changes. This static HTML integration uses Vercel's
   `/_vercel/insights/script.js` endpoint; no Node package or framework is needed.
5. Verify the script loads successfully, make a real test click on the published
   guide, and check **Analytics → Events → guide_link_click** and its properties.
   A local test does not establish that Vercel is receiving production events.

The loader runs only on HTTPS at `fallguide.nwiexplored.com`. Local file previews,
localhost and Vercel preview domains send no page views or click events. Change
the hostname allowlist deliberately if the production domain changes. The
integration also loads Vercel's normal page-view tracking on production. Review
the publisher's privacy notice before launch; the custom payload contains only
public section/item labels, not visitor details or full destination URLs.

Base Pro's custom events do not require Web Analytics Plus. Vercel's separate
incoming-UTM dashboard feature currently requires Plus or Enterprise; it is not
needed for this section/item custom-event approach.

Sources: [custom events](https://vercel.com/docs/analytics/custom-events),
[HTML setup](https://vercel.com/docs/analytics/quickstart),
[plan limits](https://vercel.com/docs/analytics/limits-and-pricing).

## Maintaining and checking the labels

Run these read-only commands from the repository (the JavaScript tests need
Node 18 or newer; the bundled Codex Node runtime was used because the system
`node` is version 12):

```sh
python3 scripts/tag_links.py --check
python3 scripts/tag_links.py --inventory
python3 scripts/check-guide.py
python3 scripts/check-tracking.py
node --test scripts/check-analytics.cjs
```

After adding, moving or renaming listings, `python3 scripts/tag_links.py --patch`
prints a reviewable patch that Codex can apply; the script itself does not write
files. It updates only web anchors and their tracking attributes, not visible copy
or original destination parameters. Unknown sections fail loudly instead of
silently receiving generic labels. Renaming an event changes its generated label
and will split historical reporting under the old and new names.

All automated tests run offline; they do not send fake events to production.

Verification: all 31 automated checks passed (16 content, 6 UTM, 9 click-handler
tests). All 189 original anchor destinations and attributes were compared with
the last commit; only the 181 web links gained UTM labels and tracking attributes.
The local browser rendered all labels with no console warnings/errors or horizontal
overflow, and did not load the production analytics script. Live dashboard
delivery remains unverified until the activation/deployment steps above.
