"""Markdown tables of the session's real-page runs beside the baseline (#1515)."""
import json, sys
NAMES = {'search': 'Search', 'guide': 'User guide', 'wiki': 'Wikipedia "Linux"', 'mdn': 'MDN `position`', 'github': 'GitHub PR 1398',
         'python': 'Python `stdtypes`', 'hn': 'HN front page', 'hnthread': 'HN thread', 'stackoverflow': 'Stack Overflow', 'news': 'Al Jazeera (cookie banner)'}
BASE = {'chromium': {'search': 'lost_track 891 / 4,220 (Google)', 'guide': 'whole, side bar repeated', 'wiki': 'lost_track 13,491 / 23,304', 'mdn': 'whole',
                     'github': 'lost_track 23,751 / 44,491', 'python': 'height_cap 52,493', 'hn': 'whole', 'hnthread': 'lost_track 8,631 and 18,351',
                     'stackoverflow': 'lost_track 891', 'news': 'lost_track 5,571 / 7,516'},
        'firefox': {'search': 'whole / failed (Bing)', 'guide': 'whole, side bar repeated', 'wiki': 'lost_track 17,779 / 24,094', 'mdn': 'whole',
                    'github': 'whole', 'python': 'height_cap 52,083', 'hn': 'whole', 'hnthread': 'lost_track 4,117',
                    'stackoverflow': 'lost_track 13,095 and 14,215', 'news': 'lost_track 1,147, then whole'}}
ORDER = list(NAMES)
rows = json.load(open(sys.argv[1]))
baseline = len(sys.argv) > 2 and sys.argv[2] == 'baseline'
print('| Page | Driver | End | Image / page px | Placed / skipped | s | Bands strict | Bands tolerant |' + (' Baseline (nightly, same desktop) |' if baseline else ''))
print('| --- | --- | --- | --- | --- | ---: | --- | --- |' + (' --- |' if baseline else ''))
for site in ORDER:
    for mode in ('user', 'auto'):
        r = next((x for x in rows if x['site'] == site and x['mode'] == mode), None)
        if not r:
            continue
        b, t = r.get('bands'), r.get('tolerant')
        cell = lambda v: '%d/%d' % tuple(v) if v else 'no reference'
        line = '| %s | %s | `%s` | %s / %s | %s / %s | %.0f | %s | %s |' % (NAMES[site], 'you scroll' if mode == 'user' else 'auto-scroll', r['end'],
                                                                       format(r['height'] or 0, ','), format(r['page'], ','), r['placed'], r['skipped'], r['seconds'], cell(b), cell(t))
        if baseline:
            line += ' %s |' % (BASE[r['browser'] if r['browser'] in BASE else 'firefox'][site] if mode == 'user' else '')
        print(line)
