#!/usr/bin/env python3
"""retire.py RUN OUTCOME FILE...: stop a lab guest of this campaign and retire its overlay with a completion manifest."""
import hashlib, json, shutil, subprocess, sys
from pathlib import Path
root = Path.home() / 'work/t1428d'
run = root / 'work/lab-runs' / sys.argv[1]
state = json.loads((run / 'state.json').read_text())
evidence = root / 'evidence' / sys.argv[1]
evidence.mkdir(parents=True)
for name in sys.argv[3:]:
    shutil.copy2(name, evidence / Path(name).name)
shutil.copy2(run / 'state.json', evidence / 'state.json')
completion = {'run': str(run), 'runId': state['id'], 'completed': True, 'outcome': sys.argv[2]}
(evidence / 'completion.json').write_text(json.dumps(completion, indent=1) + '\n')
files = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(evidence.iterdir()) if p.is_file()}
manifest = evidence.parent / (sys.argv[1] + '-manifest')
manifest.mkdir()
for p in evidence.iterdir():
    shutil.move(str(p), manifest / p.name)
evidence.rmdir()
(manifest / 'manifest.json').write_text(json.dumps(dict(completion, schemaVersion=1, kind='vm-overlay-cleanup-evidence', files=files), indent=1) + '\n')
lab = [sys.executable, str(root / 'tools/lab/lab.py')]
def call(*args):
    done = subprocess.run(lab + list(args), capture_output=True, text=True)
    print(args[0], done.returncode, (done.stdout.strip() or done.stderr.strip())[-500:], flush=True)
    return done.returncode
call('reset', '--run', str(run))
common = ['cleanup', '--run', str(run), '--evidence-manifest', str(manifest / 'manifest.json'), '--images-root', str(Path.home() / 'work/put.gd/work/lab-images')]
if call(*common, '--dry-run') == 0:
    call(*common)
print('overlay exists:', (run / 'disk.qcow2').exists())
