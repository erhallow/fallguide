#!/usr/bin/env python3
"""Create an apply_patch patch from the approved, individually authored audit edits.

Does not write the site. Asserted DOM spans preserve unrelated markup and design.
One-time generator for the fab6ad0 audit baseline, not an idempotent migration.
"""
from html import escape, unescape
from html.parser import HTMLParser
from pathlib import Path
import difflib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / 'audits/2026-09-23-extra'
original = (ROOT/'index.html').read_text()
inventory = {x['id']:x for x in json.loads((AUDIT/'inventory.json').read_text())}
reviews = {i:r for p in sorted(AUDIT.glob('reviews-*.json')) for r in json.loads(p.read_text()) for i in r['ids']}
VOID = {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}

class Spans(HTMLParser):
    def __init__(self, markup):
        super().__init__(convert_charrefs=True)
        self.markup = markup
        self.offsets = [0] + [m.end() for m in re.finditer('\n',markup)]
        self.nodes, self.stack = [], []
        self.feed(markup)
    def pos(self):
        row, col = self.getpos()
        return self.offsets[row-1]+col
    def handle_starttag(self, tag, attrs):
        start = self.pos()
        n = {'tag':tag,'attrs':dict(attrs),'start':start,'inner':start+len(self.get_starttag_text()),'parent':self.stack[-1] if self.stack else None}
        self.nodes.append(n)
        if tag in VOID:
            n.update(close=n['inner'],end=n['inner'])
        else:
            self.stack.append(n)
    def handle_endtag(self,tag):
        if self.stack and self.stack[-1]['tag']==tag:
            n=self.stack.pop(); n.update(close=self.pos(),end=self.markup.index('>',self.pos())+1)
    def select(self,predicate):
        return [n for n in self.nodes if predicate(n)]

def has(n, cls):
    return cls in n['attrs'].get('class','').split()
def txt(h,n):
    return unescape(re.sub('<[^>]+>','',h[n['inner']:n['close']])).strip()
def replace_span(h,n,value):
    return h[:n['start']]+value+h[n['end']:]
def inner(h,n,value):
    return h[:n['inner']]+value+h[n['close']:]
def class_text(h,classes,value):
    found=Spans(h).select(lambda n:any(has(n,c) for c in classes))
    assert len(found)==1, (classes,len(found),h[:150])
    return inner(h,found[0],escape(value))
def link(label,url):
    return '<a class="tl" href="'+escape(url,quote=True)+'" rel="noopener" target="_blank">'+escape(label)+'</a>'

h=original
edits=json.loads((AUDIT/'approved-edits.json').read_text())
for key,edit in edits.items():
    i=int(key); source=inventory[i]
    if source['audit_id']:
        matches=Spans(h).select(lambda n:n['attrs'].get('data-audit-id')==source['audit_id'])
        assert len(matches)==1,(i,matches)
        node=matches[0]
    else:
        matches=Spans(h).select(lambda n:n['tag']=='a' and n['attrs'].get('href')==source['url'])
        assert len(matches)==1,(i,matches)
        node=matches[0]
        while node['tag']!='li': node=node['parent']
    old=h[node['start']:node['end']]
    if edit.get('remove'):
        h=replace_span(h,node,''); continue
    block=old
    if edit.get('use_alternative'):
        old_url=escape(source['url'],quote=True); new_url=escape(reviews[i]['alternative'],quote=True)
        assert block.count('href="'+old_url+'"')==1,(i,source['url'])
        block=block.replace('href="'+old_url+'"','href="'+new_url+'"')
    if 'title' in edit:
        a=Spans(block).select(lambda n:n['tag']=='a')[0]
        block=inner(block,a,escape(edit['title']))
    for key,classes in [('meta',['ev-meta','x','w']),('note',['source-note']),('town',['town','ctown']),('tag',['tag']),('chip',['chip']),('description',['cd']),('heads',['heads'])]:
        if key in edit: block=class_text(block,classes,edit[key])
    if 'meta' in edit and 'note' not in edit:
        block=class_text(block,['source-note'],'Source reviewed Sept. 23, 2026. Check for updates before visiting.')
    if 'date' in edit:
        found=Spans(block).select(lambda n:has(n,'date') or has(n,'d'))
        assert len(found)==1
        n=found[0]
        block=replace_span(block,n,'<div class="date date-full">'+escape(edit['date'])+'</div>' if n['tag']=='div' else '<span class="d">'+escape(edit['date'])+'</span>')
    for term,value in edit.get('dd',{}).items():
        doc=Spans(block); found=doc.select(lambda n:n['tag']=='dt' and txt(block,n)==term)
        if found:
            dt=found[0]; dd=next(n for n in doc.nodes if n['tag']=='dd' and n['start']>=dt['end'])
            if value is None: block=block[:dt['start']]+block[dd['end']:]
            else: block=inner(block,dd,escape(value))
        else:
            assert value is not None
            assert block.count('</dl>')==1
            block=block.replace('</dl>','<dt>'+escape(term)+'</dt><dd>'+escape(value)+'</dd></dl>')
    for old_label,new_label in edit.get('rename_links',{}).items():
        found=Spans(block).select(lambda n:n['tag']=='a' and txt(block,n)==old_label)
        assert len(found)==1
        block=inner(block,found[0],escape(new_label))
    if edit.get('secondary'):
        doc=Spans(block); root=doc.nodes[0]
        links='<p class="source-links">'+' · '.join(link(label,url) for label,url in edit['secondary'])+'</p>'
        if root['tag']=='li' and any(has(n,'ev-meta') for n in doc.nodes):
            # Event-grid list items have a date column and one content column.
            content=[n for n in doc.nodes if n['parent'] is root and n['tag']=='div'][-1]
            block=block[:content['close']]+links+block[content['close']:]
        else: block=block[:root['close']]+links+block[root['close']:]
    h=replace_span(h,node,block)

# Remove stale historical presentation, not just the incorrect historical values.
town_node=Spans(h).select(lambda n:n['attrs'].get('id')=='town-hours')[0]
old=h[town_node['start']:town_node['end']]
tiles=Spans(old).select(lambda n:has(n,'tile'))
pending=[]
for tile in tiles:
    block=old[tile['start']:tile['end']]
    tn=Spans(block).select(lambda n:has(n,'tn'))[0]; name=txt(block,tn)
    if name=='Knox': continue
    th=Spans(block).select(lambda n:has(n,'th'))[0]; block=replace_span(block,th,'')
    block=re.sub(r'style="--c:[^"]+"','style="--c:var(--muted)"',block)
    if name=='La Porte':
        n=Spans(block).select(lambda n:has(n,'tile-source'))[0]
        block=inner(block,n,'Official source unavailable; check with the city before making plans.')
    pending.append(block)
assert len(pending)==30
town='''<section aria-labelledby="tt-h" class="panel" id="town-hours">
<div class="sec-head"><h2 id="tt-h" style="color:var(--pumpkin)">Town trick-or-treat hours</h2><span class="note">Halloween 2026 · Central Time</span></div>
<p class="lede2">Only verified <strong>2026 neighborhood trick-or-treat hours</strong> appear below. Community trunk-or-treat events and downtown business events have their own schedules.</p>
<div class="confirmed-town"><span class="chip ok">2026 confirmed</span><h3>Knox · Saturday, Oct. 31</h3><p><strong>5:30–7 p.m. Central Time</strong></p><p class="source-note"><a href="https://www.cityofknox.net/" rel="noopener" target="_blank">Official city calendar</a> · Verified Sept. 23, 2026; find the Halloween entry in the homepage calendar.</p></div>
<details class="pending-towns"><summary>Find another town — 30 schedules not yet verified</summary><p class="fine">No 2026 neighborhood hours have been verified here for these towns. Their official sites are starting points for announcements, not confirmation of a time. Check before making plans.</p><div class="tiles">
'''+ '\n'.join(pending)+'''
</div></details>
<p class="fine">Last checked Sept. 23, 2026. Westville’s Town Hall phone is provided while its website is unreliable. We do not carry last year’s hours forward as this year’s schedule.</p>
<p class="fine">Want local updates? <a href="#subscribe">See the NWI Explored newsletter offer</a>.</p></section>'''
h=replace_span(h,town_node,town)
replacements={
 'with clearly labeled historical trick-or-treat hours.':'with verified 2026 trick-or-treat hours and clear notes where details still need confirmation.',
 'plus historical town trick-or-treat hours clearly separated from 2026 plans.':'plus verified 2026 town trick-or-treat hours and a list of towns still awaiting verification.',
 '“2025 reference only” is not a confirmed 2026 schedule.':'A reviewed source is not the same as a confirmed schedule. Facebook links may show an account prompt; vendor signup is for exhibitors, not visitors.',
 '<dt>Common 2025 window</dt><dd>5–7 <small>p.m.</small></dd>':'<dt>Before heading out</dt><dd>Check updates</dd>',
 'Read a recent issue':'Read a sample issue',
}
for old,new in replacements.items():
    assert old in h,old
    h=h.replace(old,new)
# Disclose social destinations in the existing notes without adding competing CTA buttons.
for block_node in reversed(Spans(h).select(lambda n:'data-audit-id' in n['attrs'])):
    block=h[block_node['start']:block_node['end']]; doc=Spans(block)
    anchors=doc.select(lambda n:n['tag']=='a')
    if not anchors: continue
    url=anchors[0]['attrs'].get('href','')
    kind=('Facebook event' if '/events/' in url else 'Facebook post' if '/posts/' in url or 'permalink.php' in url else 'Facebook updates') if 'facebook.com' in url else 'Instagram post' if 'instagram.com' in url else None
    if kind:
        notes=doc.select(lambda n:has(n,'source-note'))
        if notes:
            n=notes[0]
            block=inner(block,n,block[n['inner']:n['close']]+' <span class="source-platform">· '+kind+'</span>')
            h=replace_span(h,block_node,block)
# Small scoped styles for source links and the new town disclosure.
h=h.replace('</style>','''.pending-towns{margin:20px 0}.pending-towns summary{cursor:pointer;font-weight:600;color:var(--rust);padding:12px 0}.pending-towns summary:focus-visible{outline:2px solid var(--plum);outline-offset:4px}.pending-towns .tiles{margin-top:12px}.trunk li>.source-links{grid-column:2}.source-platform{white-space:nowrap}
</style>''',1)
# Keep edited listing boundaries readable; the rest of the illustration markup is untouched.
h=re.sub(r'</li>(?=<li data-audit-id=)', '</li>\n',h)
diff=list(difflib.unified_diff(original.splitlines(True),h.splitlines(True),n=3))
assert diff, 'No changes generated'
print('*** Begin Patch\n*** Update File: '+str(ROOT/'index.html'))
for line in diff[2:]:
    print('@@' if line.startswith('@@') else line.rstrip('\n'))
print('*** End Patch')
