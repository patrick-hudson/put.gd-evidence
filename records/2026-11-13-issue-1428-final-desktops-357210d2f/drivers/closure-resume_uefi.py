from pathlib import Path
import sys,json
sys.path.insert(0,str(Path(__file__).parent/'r/tools/lab'));import lab
r=Path(__file__).parent/'r/work/lab-runs'/sys.argv[1];d=lab.state(r);cfg=json.loads((r/'manual-launch-config.json').read_text()) if (r/'manual-launch-config.json').exists() else lab.load_profile(d['profile'])
for s in [r/'qmp.sock',r/'vnc.sock',r/'runtime/putgd/session.sock']:assert len(str(s.resolve()).encode())<=107
with lab.overlay_cleanup.lifecycle_lock():
 p=r/'qemu.pid'
 if p.exists():p.unlink()
 a=lab.command(lab.qemu_command(cfg,r,r/'disk.qcow2',d['ssh_port'],d['vnc_display'],'kvm',d.get('firmware')),check=False);assert a.returncode==0,a.stderr
 d['pid']=int(p.read_text());lab.write_json(r/'state.json',d)
print('Owned overlay resumed',r)
