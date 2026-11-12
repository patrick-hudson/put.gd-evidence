# mkfix7.py OUT RES.json... : FIX-7.md from the head and tail texts, the collected results and the notes below.
import sys, json
from pathlib import Path
here = Path(__file__).parent
out = Path(sys.argv[1])
SITE = {'pr': '(a) pull request', 'wiki': '(b) Wikipedia', 'py': '(c) Python docs', 'mdn': '(d) MDN', 'repo': '(e) repository'}
HOST = {'d69': 'd69 Plasma', 'm74': 'm74 Cinnamon', 'f44': 'f44 GNOME'}
# Why a cell is not "complete, every band exact": by run name (prefix, browser, site, mode).
NOTE = {
    'cr-pr': 'G',
    'm74:cr-pr': 'A, G',
    'm74:cr-wiki-top': 'B',
    'm74:ff-mdn': 'C',
    'm74:ff-wiki-half': 'T: 2 bands, a paragraph drawn anew',
    'm74:ff-wiki-top': 'D',
    'f44:cr-wiki-top': 'E',
    'f44:ff-mdn-half': 'T: 1 band, a line with an emoji one row lower',
    'd69:ff-pr-half': 'S',
    'd69:ff-wiki-half': 'E',
    'd69:cr-wiki-half': 'E',
    'd69:ff-mdn': 'T: 3 bands, the rotated headings of a table',
}
rows = []
for path in sys.argv[2:]:
    for r in json.load(open(path)):
        if not r.get('site'):
            continue
        host = r['name'][:3]
        rows.append((list(SITE).index(r['site']), r['browser'], list(HOST).index(host), r['mode'], host, r))
rows.sort(key=lambda t: t[:4])
count = {}
lines = ['| Site | Browser | Desktop | Mode | Result | End reason, rows of page | Bands exact of compared | Note |', '| --- | --- | --- | --- | --- | --- | --- | --- |']
for _, _, _, _, host, r in rows:
    end, h, doc = r['end'], r['height'], r['docAfter']
    shifts = [s for s in (r['shiftChanges'] or []) if abs(s[1]) > 1]
    gap = r['browser'] == 'chromium' and r['site'] == 'pr' and len(shifts) == 1 and shifts[0][1] == 60
    if gap:
        shifts = []
    if end is None:
        cls = 'no result'
    elif shifts:
        cls = '**wrong**'
    elif end == 'end_of_content' and doc and h >= doc - 3:
        cls = 'complete'
    elif end == 'height_cap':
        cls = 'capped'
    elif end == 'end_of_content':
        cls = '**short**'
    else:
        cls = 'honest partial'
    count[cls] = count.get(cls, 0) + 1
    b = 'cr' if r['browser'] == 'chromium' else 'ff'
    keys = ['%s:%s-%s-%s' % (host, b, r['site'], r['mode']), '%s:%s-%s' % (host, b, r['site']), '%s-%s' % (b, r['site'])]
    note = next((NOTE[k] for k in keys if k in NOTE), '')
    exact = (r['exactBands'] or 0) + ((r['shiftedBands'] or 0) if gap else 0)
    if not note and (r['badBands'] or r['shiftedBands']):
        note = '**unexplained: %s bands differ, %s shifted**' % (r['badBands'], r['shiftedBands'])
    lines.append('| %s | %s | %s | %s | %s | `%s`, %s of %s | %s of %s | %s |' % (
        SITE[r['site']], r['browser'].capitalize(), HOST[host], 'halfway, to the top' if r['mode'] == 'half' else 'from the top', cls, end,
        '{:,}'.format(h) if h else '-', '{:,}'.format(doc) if doc else '-', exact, r['bands'], note))
total = sum(count.values())
summary = ', '.join('%d %s' % (n, k.replace('*', '')) for k, n in sorted(count.items(), key=lambda kv: -kv[1]))
text = (here / 'FIX-7.head.md').read_text() + '\n' + (here / 'FIX-7.results.md').read_text().replace('@TABLE@', '\n'.join(lines)).replace('@SUMMARY@', '%d captures: %s' % (total, summary)) + '\n' + (here / 'FIX-7.tail.md').read_text()
for k, v in json.loads((here / 'FIX-7.values.json').read_text()).items():
    text = text.replace('@' + k + '@', v)
left = sorted({w for w in text.split() if w.startswith('@') and w.endswith('@') and len(w) > 2})
out.write_text(text)
print('%d captures: %s' % (total, summary), '| placeholders left:', left)
