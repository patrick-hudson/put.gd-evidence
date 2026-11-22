"""Write completion.json + manifest for a custom run and print the manifest path: retire.py RUN EVDIR OUTCOME"""
import hashlib, json, sys
from pathlib import Path
run, ev, outcome = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve(), sys.argv[3]
ev.mkdir(parents=True, exist_ok=True)
rid = json.loads((run / 'state.json').read_text())['id'] if (run / 'state.json').exists() else None
if rid is None:
    for p in run.glob('*.json'):
        try:
            d = json.loads(p.read_text())
            if isinstance(d, dict) and 'id' in d and 'vnc_display' in d: rid = d['id']; break
        except Exception: pass
c = {'run': str(run), 'runId': rid, 'completed': True, 'outcome': outcome}
(ev / 'completion.json').write_text(json.dumps(c, indent=1))
files = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in ev.iterdir() if p.is_file() and p.name != 'manifest.json'}
(ev / 'manifest.json').write_text(json.dumps({'schemaVersion': 1, 'kind': 'vm-overlay-cleanup-evidence', **c, 'files': files}, indent=1))
print(ev / 'manifest.json', rid)
