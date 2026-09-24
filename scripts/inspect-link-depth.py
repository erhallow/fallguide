#!/usr/bin/env python3
"""Print focused saved evidence for manual review; no network or mutations."""
import json
from pathlib import Path
import re
import sys

root = Path(__file__).resolve().parents[1] / 'audits/2026-09-23-extra'
links = json.loads((root/'inventory.json').read_text())
pages = {r['url']:r for r in json.loads((root/'retrievals.json').read_text())}
ids = set()
for part in sys.argv[1].split(','):
    if '-' in part:
        a,b = map(int,part.split('-')); ids.update(range(a,b+1))
    else: ids.add(int(part))
limit = int(sys.argv[2]) if len(sys.argv)>2 else 5000
for link in links:
    if link['id'] not in ids: continue
    p = pages.get(link['url'],{})
    print('\n###', link['id'], link['label'], '|', link['url'])
    print('GUIDE:',link['guide'])
    print('FETCH:',p.get('status',p.get('error')),p.get('final_url',''))
    body = p.get('text','')
    if '--focus' in sys.argv:
        lines = body.splitlines()
        keep = set(range(min(4,len(lines))))
        for i,line in enumerate(lines):
            if re.search(r'202[456]|\\d.*(?:a\\.?m|p\\.?m|:|mile|acre|feet|road|ave|street)|\\$|Sept|Oct|Nov|closed|free|admission|ages|price|date|hours|schedule|hallow|trunk|treat|parking|wheelchair|rugged',line,re.I):
                keep.update(range(max(0,i-1),min(len(lines),i+3)))
        body='\n'.join(lines[i] for i in sorted(keep))
    print(body[:limit])
    candidates = [l for l in p.get('links',[]) if re.search('hallow|trunk|treat|pumpkin|fall|october|2026|hours|admission|tickets|hayride|trail|visit|boo|candlelight|superstition',l['label']+' '+l['url'],re.I) and len(l['label'].strip())>2 and len(l['url'])<300 and not re.search('wp-login|sharer|calendar/event|outlook|signin|login|shareArticle',l['url'])]
    unique = {l['url']: {'url':l['url'],'label':' '.join(l['label'].split())[:120]} for l in candidates}
    print('CANDIDATE LINKS:',json.dumps(list(unique.values())[:30],ensure_ascii=False))
