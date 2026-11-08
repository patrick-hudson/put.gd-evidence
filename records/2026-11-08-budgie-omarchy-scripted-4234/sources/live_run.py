import sys,os,json,uuid,subprocess
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
from tools.lab import lab,nightly_desktops as n,nightly_desktop_guest as g
run,out,desktop,package,host,destination=sys.argv[1:];run=Path(run).resolve();out=Path(out);out.parent.mkdir(mode=0o700,exist_ok=True)
session='sp1275-'+uuid.uuid4().hex[:12];slot=Path.home()/'putgd-lab/locks/tier1-guest.lock.d';slot.mkdir(mode=0o700)
n.save(slot/'owner.json',dict(run=str(run),session=session,worker=n.worker_identity(),evidence=str(out)))
(slot/'session').write_text(session+'\n');(slot/'session').chmod(0o600)
try:
 keyout=out.with_name(out.name+'-keys');keyout.mkdir(mode=0o700)
 if not lab.state(run).get('secret_service'):g.prepare_live_keyring(run,keyout)
 args=[sys.executable,'-u','work/sp/pass.py',str(run),str(out),desktop,package,host,destination]
 if destination=='proton':args=[sys.executable,'tools/lab/proton_lab.py','lend',str(run),'--session',session,'--owner','sp1275','--purpose','private scripted outcomes on published nightly4234','--']+args
 r=subprocess.run(args,env=dict(os.environ,PUTGD_TIER1_SESSION=session));assert r.returncode==0,'script returned nonzero; preserve run evidence'
finally:
 if 'r' not in locals() or r.returncode!=0:
  n.save(slot/'retained.json',dict(run=str(run),session=session,evidence=str(out)))
  raise RuntimeError('script failed; owned guest slot retained for recovery')
 assert (slot/'session').read_text().strip()==session
 (slot/'session').unlink();(slot/'owner.json').unlink();slot.rmdir()
