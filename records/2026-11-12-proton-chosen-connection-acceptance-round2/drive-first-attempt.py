#!/usr/bin/env python3
import subprocess as s, pathlib as P, sys, time, json, shutil
BASE=P.Path('/tmp/pr1414r2'); ORIG=BASE/'records/2026-11-12-proton-chosen-connection-acceptance'
host=sys.argv[1]; ip={'d69':69,'k72':72,'m74':74,'f44':70}[host]; session='p1414-ec6-'+host
ssh=['ssh','-i','/home/patrick/.ssh/awskey_110724','-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','-o','BatchMode=yes','-o','ConnectTimeout=15','-o',f'UserKnownHostsFile=/home/patrick/work/put.gd/work/remote-builders/{host}/known_hosts',f'patrick@192.168.68.{ip}']
scp=['scp','-q']+ssh[1:-1]; lock=[sys.executable,str(BASE/'desktop_lock.py')]
out=BASE/host; out.mkdir()
def cmd(a,**kw):return s.run(a,check=True,**kw)
def remote(c,**kw):return cmd(ssh+[c],**kw)
def lease(action,res='desktop',**kw):return s.run(lock+[action,host,'--resource',res,'--session',session]+kw.get('extra',[]),check=True)
# Locks acquired sequentially, checked; no activity if either refused.
lease('acquire',extra=['--owner','proton-round2','--purpose','PR1414 exact-head acceptance; notes /tmp/pr1414r2','--minutes','45'])
try: lease('acquire','proton',extra=['--owner','proton-round2','--purpose','PR1414 round2 control','--minutes','45'])
except: lease('release',extra=['--verified-clean']);raise
import threading
stop=threading.Event()
def heartbeat():
 while not stop.wait(60):
  for res in ('desktop','proton'):lease('heartbeat',res)
t=threading.Thread(target=heartbeat,daemon=True);t.start()
try:
 with (out/'environment.txt').open('w') as envlog:
  remote('uname -a; cat /etc/os-release; uptime; dpkg-query -W plasma-workspace kwin-wayland cinnamon 2>/dev/null; rpm -q gnome-shell mutter 2>/dev/null; true',stdout=envlog)
 remote('mkdir -m 700 ~/work/pecr2')
 kind='debian13' if host=='d69' else 'ubuntu26.04' if host=='k72' else 'AppImage'
 pr=next(p for p in (BASE/'packages').rglob('*') if p.is_file() and (kind in str(p)) and p.suffix in ('.deb','.AppImage'))
 nc=next(p for p in (BASE/'nightly').iterdir() if kind in p.name and p.suffix in ('.deb','.AppImage'))
 cmd(scp+[str(pr),str(nc),str(ORIG/'proton_accept.py'),str(ORIG/'run_accept.sh'),str(BASE/'round2.py'),str(BASE/'desktop_lock.py'),ssh[-1]+':work/pecr2/'])
 def extract(f,d):
  return f'mkdir {d} && '+(f'dpkg-deb -x {f.name} {d}' if f.suffix=='.deb' else f'chmod 700 {f.name} && (cd {d} && ../{f.name} --appimage-extract >/dev/null)')
 remote('cd ~/work/pecr2 && '+extract(pr,'app')+' && '+extract(nc,'night-app'))
 root='app' if pr.suffix=='.deb' else 'app/squashfs-root'
 with (out/'run.log').open('w') as log:
  r=s.run(ssh+[f'cd ~/work/pecr2 && uptime && python3 round2.py --app {root} --work pr --host {host} --session {session}'],stdout=log,stderr=s.STDOUT)
 (out/'exit.json').write_text(json.dumps({'exit':r.returncode}))
 # Copy only explicit run output paths; raw stays private.
 with (out/'raw.tar').open('wb') as f:remote('cd ~/work/pecr2 && tar -cf - pr nc nightly-run.log',stdout=f)
 cmd(['tar','-xf',str(out/'raw.tar'),'-C',str(out)])
 remote("python3 - <<'PY2'\nimport os\nfrom pathlib import Path\nfor p in Path('/proc').iterdir():\n if not p.name.isdigit():continue\n try:\n  if p.stat().st_uid==os.getuid() and ((p/'comm').read_text().startswith('putgd') or b'/work/pecr2/' in (p/'cmdline').read_bytes()):print(p.name,(p/'comm').read_text().strip())\n except OSError:pass\nPY2")
finally:
 stop.set();t.join()
 lease('release','proton',extra=['--verified-clean'])
 lease('release')
 lease('release',extra=['--verified-clean'])
