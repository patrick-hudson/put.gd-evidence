import sys,json,time,shlex
from pathlib import Path
from PIL import Image
sys.path.insert(0,'/home/patrick/work/pg-cd/tools/lab');import lab
r='/home/patrick/work/pg-cd/work/lab-runs/bc7';out=Path(r)/'accept';out.mkdir(exist_ok=True)
def shell(s):return lab.guest_session(r,s)
def capture(name):
 start=time.monotonic();oid=lab.cli(r,'action.invoke',{'action':'desktop'})['operationId']
 for _ in range(150):
  op=next(o for o in lab.cli(r,'operation.recent')['operations'] if o['id']==oid)
  if op['state'] in ('completed','failed','cancelled'):break
  time.sleep(.1)
 row={'milliseconds':round((time.monotonic()-start)*1000),'operation':op}
 (out/(name+'.json')).write_text(json.dumps(row,indent=2));print(name,op['state'],op['error']['code'],row['milliseconds'],flush=True)
 if op['state']=='completed':lab.get(r,op['items'][0]['local']['path'],out/(name+'.png'))
 return row
def shot(name):Image.open(lab.screenshot(r,name)['path']).save(out/(name+'.png'))
if len(sys.argv)>1 and sys.argv[1]=='after-unlock':
 row=capture('unlocked-after');assert row['operation']['state']=='completed';shot('unlocked-after-witness');sys.exit()
(out/'install.json').write_text(json.dumps(lab.install(r,appimage='/tmp/pg-c-three.AppImage'),indent=2))
(out/'start.json').write_text(json.dumps(lab.start(r),indent=2))
v=json.loads(shell('putgd-cli --version-json'));expected=json.loads(Path('/tmp/pg-c-three-build-info.json').read_text());assert v==expected
(out/'version.json').write_text(json.dumps(v,indent=2));(out/'capabilities.json').write_text(json.dumps(lab.cli(r,'capabilities'),indent=2))
paths=lab.ssh(r,"python3 - <<'CHECK'\nfrom pathlib import Path\nimport json\np=['/run/user/1000/putgd/session.sock','/run/user/1000/bus']+[str(p) for p in Path('/run/user/1000').glob('wayland-*') if not p.name.endswith('.lock')]\nassert all(len(s.encode())<=107 for s in p)\nprint(json.dumps({s:len(s.encode()) for s in p}))\nCHECK")
(out/'socket-paths.json').write_text(paths)
s=lab.cli(r,'settings.get');lab.cli(r,'settings.patch',{'expectedRevision':s['metadata']['acceptedRevision'],'patch':{'actions':{a:{'destination':'local','shortcut':''} for a in ('region','window','desktop','clipboard','edit')},'profiles':[],'archive':{'root':'/home/lab/pg-evidence/captures','keepUploads':True},'preferences':{'notifications':False}}})
lab.put(r,'/tmp/pg-load.html','/home/lab/pg-load.html')
start_script='''import subprocess,json,os
from pathlib import Path
p=Path('/home/lab/pg-load-profile');p.mkdir(mode=0o700)
(p/'user.js').write_text('user_pref("browser.shell.checkDefaultBrowser", false);user_pref("browser.startup.homepage_override.mstone", "ignore");user_pref("datareporting.policy.dataSubmissionEnabled", false);user_pref("toolkit.telemetry.enabled", false);')
log=open('/tmp/pg-firefox-load.log','w')
env=dict(os.environ,MOZ_ENABLE_WAYLAND='1')
child=subprocess.Popen(['firefox','--no-remote','--profile',str(p),'--kiosk','file:///home/lab/pg-load.html'],stdout=log,stderr=subprocess.STDOUT,start_new_session=True,env=env)
ticks=Path('/proc/'+str(child.pid)+'/stat').read_text().rsplit(')',1)[1].split()[19]
Path('/tmp/pg-browser.json').write_text(json.dumps({'pid':child.pid,'startTicks':ticks}))
print(json.dumps({'pid':child.pid,'startTicks':ticks}))
'''
cpu_script="import json;v=list(map(int,open('/proc/stat').readline().split()[1:]));print(json.dumps({'total':sum(v),'idle':v[3]+v[4]}))"
def cpu():return json.loads(shell('python3 -c '+shlex.quote(cpu_script)))
before=cpu();(out/'browser-start.json').write_text(shell('python3 - <<\'START\'\n'+start_script+'\nSTART'))
rows=[]
for i in range(10):
 row=capture('loaded-'+str(i));rows.append(row);assert row['operation']['state']=='completed'
 if i==4:shot('loaded-witness')
after=cpu();(out/'loaded-results.json').write_text(json.dumps(rows,indent=2))
(out/'load-metrics.json').write_text(json.dumps({'before':before,'after':after,'guestBusyPercent':round(100*(1-(after['idle']-before['idle'])/(after['total']-before['total'])),1),'note':'Two-vCPU guest; Firefox started immediately before capture0 and animates9000 rectangles per frame throughout the ten consecutive requests.'},indent=2))
(out/'load-processes.txt').write_text(shell('ps -u lab -o pid,ppid,comm,pcpu; cat /proc/loadavg; rpm -q firefox labwc budgie-desktop gtklock'))
stop_script='''import json,os,signal,time
from pathlib import Path
r=json.loads(Path('/tmp/pg-browser.json').read_text());p=Path('/proc/'+str(r['pid']))
assert p.stat().st_uid==os.getuid() and p.joinpath('stat').read_text().rsplit(')',1)[1].split()[19]==r['startTicks']
assert b'/home/lab/pg-load-profile' in p.joinpath('cmdline').read_bytes()
parents={};starts={}
for f in Path('/proc').iterdir():
 if not f.name.isdigit():continue
 try:
  a=(f/'stat').read_text().rsplit(')',1)[1].split();parents[int(f.name)]=int(a[1]);starts[int(f.name)]=a[19]
 except (OSError,IndexError):pass
owned={r['pid']}
while True:
 more={pid for pid,parent in parents.items() if parent in owned};n=len(owned);owned.update(more)
 if len(owned)==n:break
for pid in sorted(owned,key=lambda pid:pid!=r['pid']):
 try:
  f=Path('/proc/'+str(pid));a=(f/'stat').read_text().rsplit(')',1)[1].split()
  if f.stat().st_uid==os.getuid() and a[19]==starts[pid]:os.kill(pid,signal.SIGTERM)
 except (OSError,IndexError):pass
print(json.dumps({'terminatedExactPids':sorted(owned)}))
'''
(out/'browser-stop.json').write_text(shell('python3 - <<\'STOP\'\n'+stop_script+'\nSTOP'));time.sleep(.5)
def state():return shell('wlopm; loginctl show-session 1 -p LockedHint; if pgrep -x gtklock >/dev/null; then echo gtklock-present; else echo gtklock-absent; fi')
(out/'blank-before.txt').write_text(state());shell("wlopm --off '*'");time.sleep(.3)
(out/'blank-state.txt').write_text(state());before_files=lab.ssh(r,'find /home/lab/pg-evidence/captures -type f | sort')
try:blank=capture('blanked-unlocked')
finally:shell("wlopm --on '*'")
(out/'blank-files.json').write_text(json.dumps({'before':before_files.splitlines(),'after':lab.ssh(r,'find /home/lab/pg-evidence/captures -type f | sort').splitlines()},indent=2))
(out/'blank-restored.txt').write_text(state());assert capture('power-restored')['operation']['state']=='completed'
shell('busctl --user call org.buddiesofbudgie.BudgieScreenlock /org/buddiesofbudgie/Screenlock org.buddiesofbudgie.BudgieScreenlock Lock');time.sleep(1);shot('locked')
(out/'locked-state.txt').write_text(state());before_files=lab.ssh(r,'find /home/lab/pg-evidence/captures -type f | sort')
for i in range(3):
 row=capture('locked-'+str(i));op=row['operation'];assert op['state']=='failed' and op['error']['code']=='session_locked' and not op['items']
after_files=lab.ssh(r,'find /home/lab/pg-evidence/captures -type f | sort');assert before_files==after_files
(out/'locked-no-new-files.json').write_text(json.dumps({'unchanged':True,'before':before_files.splitlines(),'after':after_files.splitlines()},indent=2))
