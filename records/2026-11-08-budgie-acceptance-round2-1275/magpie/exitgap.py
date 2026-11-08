import json, glob, sys
from datetime import datetime
def t(s): return datetime.fromisoformat(s.replace('Z', '+00:00'))
for run in sys.argv[1:]:
    ev = []
    for f in glob.glob(run + '/state/putgd/logs/*.jsonl'):
        for l in open(f):
            d = json.loads(l); ev.append(d)
    ev.sort(key=lambda d: d['time'])
    cancel = None; out = []
    for d in ev:
        m = d['message']; fl = d.get('fields', {})
        if m == 'Operation finished' and fl.get('state') == 'cancelled': cancel = t(d['time'])
        if m == 'Recording failed': out.append(('refused', fl.get('error', {}).get('code'), round((t(d['time']) - cancel).total_seconds() * 1000) if cancel else None))
        if m == 'Helper exited' and fl.get('helper') == 'putgd-record' and cancel: out.append(('old helper exit after cancel ms', round((t(d['time']) - cancel).total_seconds() * 1000))); cancel = None
    print(run, out)
