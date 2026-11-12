# prog.py PREFIX : one line per finished run of a campaign, from its console
import sys, json
from pathlib import Path
for l in (Path.home() / 'work/sf7' / (sys.argv[1] + '.console')).read_text(errors='replace').splitlines():
    if l.startswith('{"name"'):
        o = json.loads(l)
        print('%-20s %-15s %6s of %6s %6ss %s' % (o['name'], o['end'], o['height'], o['doc'], o['seconds'], str(o.get('note') or o.get('failed') or '')[:90]))
    elif l.startswith('ERROR'):
        print(l[:200])
