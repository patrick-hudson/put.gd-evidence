from pathlib import Path
import sys,json,time,shutil
sys.path.insert(0,str(Path.home()/'work/s52/tools/lab'));import lab
r=Path.home()/'work/s52/work/lab-runs/h3';s=lab.state(str(r));shutil.copyfile(r/'state.json',Path.home()/'work/s5302/h-state-before-nightly-restart.json')
assert not Path('/proc/'+str(s['pid'])).exists()
for n in ['qmp.sock','vnc.sock']:assert len(str(r/n).encode())<=107
p=lab.load_profile(s['profile']);q=lab.command(lab.qemu_command(p,r,Path(s['overlay']),s['ssh_port'],s['vnc_display'],s['acceleration'],s.get('firmware'),1),timeout=15,check=False)
assert q.returncode==0,q.stderr
s['pid']=int((r/'qemu.pid').read_text());lab.write_json(r/'state.json',s);print('owned overlay restarted',s['id'],s['pid'],flush=True)
for _ in range(100):
 try:
  lab.ssh(str(r),'true\n',timeout=5);break
 except Exception:time.sleep(2)
else:raise RuntimeError('SSH did not return')
print(json.dumps(lab.guest_preflight(str(r),apply=True,stage='nightly-control-restart')),flush=True)
