#!/usr/bin/env python3
"""Snapshot every anchor and retrieve public pages for a manual link-depth review."""
import concurrent.futures
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import runpy
import sys
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'audits' / '2026-09-23-extra'

class Page(HTMLParser):
    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.skip = 0
        self.parts = []
        self.links = []
        self.active = None
        self.feed(html)
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in {'script', 'style', 'noscript', 'svg'}:
            self.skip += 1
        if tag == 'a' and attrs.get('href'):
            self.active = {'url': attrs['href'], 'label': ''}
            self.links.append(self.active)
        if tag == 'img' and attrs.get('alt'):
            self.parts.append('[image: ' + attrs['alt'] + ']')
        if tag in {'p','div','li','h1','h2','h3','h4','br','section'}:
            self.parts.append('\n')
    def handle_endtag(self, tag):
        if tag in {'script', 'style', 'noscript', 'svg'}:
            self.skip = max(0, self.skip - 1)
        if tag == 'a':
            self.active = None
    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)
            if self.active:
                self.active['label'] += data
    def text(self):
        return '\n'.join(s for line in ''.join(self.parts).splitlines() if (s := ' '.join(line.split())))

def inventory():
    doc = runpy.run_path(str(ROOT / 'scripts/check-guide.py'))['DOC']
    result = []
    for n in doc.nodes:
        if n.tag != 'a' or 'href' not in n.attrs:
            continue
        parent = n
        while parent.parent and not (parent.tag in {'li','footer'} or parent.attrs.get('data-audit-id') or parent.has_class('tile') or parent.has_class('sub-section') or parent.has_class('sub-slot')):
            parent = parent.parent
        context = parent.text if parent.tag != 'document' else n.text
        result.append({'id':len(result)+1, 'audit_id':parent.attrs.get('data-audit-id'), 'label':' '.join(n.text.split()), 'url':n.attrs['href'], 'guide':' '.join(context.split())})
    return result

def fetch(url):
    key = hashlib.sha256(url.encode()).hexdigest()[:16]
    r = {'url':url,'key':key}
    try:
        req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0 (compatible; FallGuideLinkReview/1.0)'})
        with urllib.request.urlopen(req, timeout=25) as response:
            raw = response.read(50000001)
            if len(raw) > 50000000:
                raise ValueError('Public source exceeds 50 MB review limit; not saved as a complete document')
            r.update(status=response.status, final_url=response.url, content_type=response.headers.get('Content-Type',''))
        if 'pdf' in r['content_type'] or raw.startswith(b'%PDF'):
            (OUT / 'evidence' / (key+'.pdf')).write_bytes(raw)
            r['text'] = '[PDF — requires visual review]'
        else:
            html = raw.decode('utf-8', errors='replace')
            page = Page(html)
            r.update(text=page.text(), links=page.links)
            (OUT / 'evidence' / (key+'.txt')).write_text(r['text'])
    except Exception as e:
        r.update(error=str(e),text='')
    return r

if __name__ == '__main__':
    OUT.mkdir(exist_ok=True, parents=True)
    (OUT / 'evidence').mkdir(exist_ok=True)
    if '--additional' in sys.argv:
        for url in sys.argv[sys.argv.index('--additional')+1:]:
            result = fetch(url)
            (OUT / 'evidence' / (result['key']+'.json')).write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
            print(json.dumps(result,ensure_ascii=False),flush=True)
        sys.exit(0)
    links = inventory()
    (OUT / 'inventory.json').write_text(json.dumps(links,indent=2,ensure_ascii=False)+'\n')
    print(f'{len(links)} anchors; {len(set(x["url"] for x in links if x["url"].startswith("http")))} unique external URLs', flush=True)
    if '--inventory' not in sys.argv:
        urls = list(dict.fromkeys(x['url'] for x in links if x['url'].startswith('http')))
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
            results = list(pool.map(fetch, urls))
        (OUT / 'retrievals.json').write_text(json.dumps(results,indent=2,ensure_ascii=False)+'\n')
        print(json.dumps([{'url':r['url'],'status':r.get('status'), 'error':r.get('error'), 'chars':len(r['text'])} for r in results],indent=2),flush=True)
