#!/usr/bin/env python3
"""Assemble manually reviewed findings, requiring exactly one review per anchor."""
import json
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'audits' / '2026-09-23-extra'
inventory = json.loads((OUT / 'inventory.json').read_text())
reviews = [r for p in sorted(OUT.glob('reviews-*.json')) for r in json.loads(p.read_text())]
counts = Counter(i for r in reviews for i in r['ids'])
expected = set(range(1, len(inventory) + 1))
assert set(counts) == expected, f'Missing: {expected-set(counts)}; extra: {set(counts)-expected}'
assert all(n == 1 for n in counts.values()), f'Duplicate review IDs: {counts}'
by_id = {i: r for r in reviews for i in r['ids']}
towns = ['Cedar Lake','Chesterton','Crown Point','DeMotte','Dyer','East Chicago','Gary','Griffith','Hammond','Hebron','Highland','Hobart','Knox','Kouts','La Porte','Lake Station','Lowell','Merrillville','Michigan City','Munster','North Judson','Portage','Porter','Rensselaer','Schererville','St. John','Valparaiso','Westville','Wheatfield','Whiting','Winfield']
sections = {1:'Navigation, newsletter and sunset reference',9:'Festivals, events and markets',69:'Trunk-or-treat and community Halloween events',99:'Haunts, hayrides and ghost tours',114:'Municipal Halloween-hours sources',146:'Newsletter navigation',148:'Farms, orchards and pumpkin patches',165:'Hiking and preserve sources',183:'Closing calls to action and footer'}
def title(link):
    i = link['id']
    if 115 <= i <= 145:
        return f'{towns[i-115]} — {link["label"]}'
    if i == 114:
        return 'Knox — confirmed city-calendar link'
    return link['label']
def target(url):
    return 'https://fallguide.nwiexplored.com/' + url if url.startswith('#') else url
def md(label, url):
    return '[' + label.replace('[','').replace(']','') + '](' + url + ')'
lines = [
    '# Fall Guide — complete link-by-link review', '',
    'Review snapshot: September 23, 2026. Site: [fallguide.nwiexplored.com](https://fallguide.nwiexplored.com/). Repository main at `fab6ad016e946228a87e218fb5d5126715fa3151`.', '',
    '**Coverage:** 186 anchor occurrences: 179 outbound web links representing 159 unique web URLs, six internal navigation links, and one telephone link. Duplicate destinations are assessed in each guide context. All 186 have a recorded finding; this does not mean every destination or event could be verified.', '',
    '**Scope:** read-only content/link review. No guide changes, commits or pushes. See [priority findings and approval list](./report.md) first.', '',
    '## How to read this audit', '',
    '- **Match** means the relevant details available on the source agree with the guide; it is not a guarantee the organizer will not change them.',
    '- **Direct** permits normal scrolling on a specific event page. **Hunt** means searching a homepage/feed, unrelated events or a general calendar. An extra click for tickets is normal; an extra search to find the event is not.',
    '- **Unverified / blocked** means this review could not establish the facts, not that the event is canceled. Login gates, blank JavaScript pages, source contradictions and browser certificate errors are identified explicitly.',
    '- Public pages were reviewed through text retrieval, browser inspection for dynamic/social/problematic pages, and visual inspection of selected PDF/flyer details. Not every page was visually inspected. Search snippets were discovery leads, not final proof when live pages disagreed or could not open.',
    '- A footer year or calendar selector was not treated as an event year. Historical town hours and separate trunk-or-treat events were not used to confirm Halloween neighborhood hours.',
    '- Alternatives are labeled as organizer, venue, municipal/community or secondary listings in the findings. A candidate is not a verified replacement. No accounts were created, calls made, forms submitted or tickets purchased.', '',
    '## Contents', '',
]
for first, section in sections.items():
    lines.append(f'- [{section}](#link-{first})')
lines += ['', '## At-a-glance index', '', '| # | Guide link / context | Accuracy | Findability |', '|---|---|---|---|']
for link in inventory:
    r = by_id[link['id']]
    lines.append(f'| {link["id"]} | [{title(link).replace("|", "/")}](#link-{link["id"]}) | {r["accuracy"]} | {r["ease"]} |')
for link in inventory:
    i = link['id']; r = by_id[i]
    if i in sections:
        lines += ['', '## ' + sections[i], '']
    lines += [f'<a id="link-{i}"></a>', '', f'### {i}. {title(link)}', '',
              'Current destination: ' + md(link['label'],target(link['url'])), '',
              f'**Accuracy:** {r["accuracy"]}. **Findability:** {r["ease"]}.', '',
              r['review'], '', '**Recommendation:** ' + r['action'], '']
    if r.get('alternative'):
        lines += ['Reviewed alternative / supporting detail: ' + md('Open source',r['alternative']), '']
    if r.get('source'):
        lines += ['Supporting historical source (not 2026 confirmation): ' + md('Open official document',r['source']), '']
    if r.get('candidate'):
        lines += ['Candidate only — not a verified replacement: ' + md('Open candidate',r['candidate']), '']
    if not any(r.get(k) for k in ('alternative','source','candidate')):
        lines += ['**Alternative result:** ' + ('No verified better replacement found in this review; see the recommendation above.' if any(t in r['ease'].lower() for t in ('hunt','blocked','login','vendor','missing','extra')) else 'Current link is retained; any remaining source limitations are noted above.'), '']
(OUT / 'link-by-link.md').write_text('\n'.join(lines).rstrip()+'\n')
print(f'Coverage validated: {len(counts)}/{len(inventory)} anchors, each exactly once.')
print(f'Review groups with an alternative/supporting-detail URL: {sum(bool(r.get("alternative")) for r in reviews)}')
print(f'Full report: {OUT / "link-by-link.md"}')
