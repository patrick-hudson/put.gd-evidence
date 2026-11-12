# mktable.py RES.json... : the site table of FIX-7 from collect7.py's output, one row per run, with a first classification.
import sys, json
SITE = {'pr': '(a) pull request', 'wiki': '(b) Wikipedia', 'py': '(c) Python docs', 'mdn': '(d) MDN', 'repo': '(e) repository'}
HOST = {'d69': 'd69 Plasma', 'm74': 'm74 Cinnamon', 'f44': 'f44 GNOME'}
rows = []
for path in sys.argv[1:]:
    for r in json.load(open(path)):
        if not r.get('site'):
            continue
        host = r['name'][:3]
        rows.append((list(SITE).index(r['site']) if r['site'] in SITE else 9, r['browser'] or '', list(HOST).index(host), r['mode'] or '', host, r))
rows.sort(key=lambda t: t[:4])
print('| Site | Browser | Desktop | Mode | Result | End, rows of page | Bands exact / compared | Not exact |')
print('| --- | --- | --- | --- | --- | --- | --- | --- |')
for _, _, _, _, host, r in rows:
    end, h, doc = r['end'], r['height'], r['docAfter']
    shifts = [s for s in (r['shiftChanges'] or []) if abs(s[1]) > 1]
    # The Chromium reference of the pull request page has 60 rows the page does not: the harness turns the page's
    # sticky bar into a relative one for the picture, and where the page has it, it then takes room. One shift of 60.
    gap = r['browser'] == 'chromium' and r['site'] == 'pr' and len(shifts) == 1 and shifts[0][1] == 60
    if gap:
        shifts = []
    bad = r['badBands'] or 0
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
    notes = []
    if gap:
        notes.append('%d bands exact 60 rows on in the reference (its own gap, see below)' % r['shiftedBands'])
    elif r['shiftedBands']:
        notes.append('%d bands found %s rows off' % (r['shiftedBands'], ', '.join(str(s[1]) for s in (r['shiftChanges'] or [])[:3])))
    if bad:
        xs = sorted({tuple(b.get('x') or []) for b in (r['bad'] or [])})
        notes.append('%d bands differ (x %s)' % (bad, '; '.join('%d-%d' % x for x in xs[:3] if len(x) == 2)))
    if r.get('note'):
        notes.append(r['note'][:90])
    print('| %s | %s | %s | %s | %s | `%s`, %s of %s | %s / %s | %s |' % (SITE.get(r['site'], r['site']), (r['browser'] or '').capitalize(), HOST[host], 'halfway, to top' if r['mode'] == 'half' else 'from top',
          cls, end, '{:,}'.format(h) if h else '-', '{:,}'.format(doc) if doc else '-', (r['exactBands'] or 0) + (r['shiftedBands'] or 0 if gap else 0), r['bands'], '; '.join(notes) or ''))
