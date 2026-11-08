import sys,json
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
from tools.lab import lab
run=Path('work/lab-runs/np3').resolve();batch=Path('work/np/r3b');assert json.loads((batch/'result.json').read_text()).get('finishedAt')
assert not (Path.home()/'putgd-lab/locks/tier1-guest.lock.d').exists()
for receipt in batch.glob('*/receipt.json'):
 e=json.loads(receipt.read_text())['environment'];assert not e.get('cleanup_errors') and e.get('private_cleanup')=='resident-log-and-state-root-removed'
lab.verify_owned_guest(run)
script='''import json,os,signal,subprocess,time
from pathlib import Path
pid=22438;expected='374127';p=Path('/proc')/str(pid)
assert p.stat().st_uid==os.getuid()
assert (p/'stat').read_text().split(') ',1)[1].split()[19]==expected
args=(p/'cmdline').read_bytes().split(b'\\0');assert Path(args[0].decode()).name=='hyprland-preview-share-picker' and args[1]==b'--allow-token'
def layers():return json.loads(subprocess.check_output(['hyprctl','layers','-j']))
before=layers();found=[l for monitor in before.values() for level in monitor['levels'].values() for l in level if l['pid']==pid]
assert len(found)==1 and found[0]['namespace']=='ch.wysbd.hyprland-preview-share-picker'
fd=os.pidfd_open(pid)
assert (p/'stat').read_text().split(') ',1)[1].split()[19]==expected
signal.pidfd_send_signal(fd,signal.SIGTERM);os.close(fd)
for _ in range(50):
 after=layers()
 if not any(l['pid']==pid for m in after.values() for level in m['levels'].values() for l in level):break
 time.sleep(.1)
else:raise RuntimeError('orphan picker layer did not retire')
print(json.dumps({'run':'np3','pid':pid,'start':expected,'name':'hyprland-preview-share-picker','priorRecipesTerminalAndClean':True,'signal':'SIGTERM via verified pidfd','beforeLayers':before,'afterLayers':after,'orphanLayerRemoved':True}))
'''
result=lab.guest_session(run,"python3 - <<'PY'\n"+script+"\nPY\n");Path('work/np/r3-picker-cleanup.json').write_text(result);print('verified orphan picker removed')
