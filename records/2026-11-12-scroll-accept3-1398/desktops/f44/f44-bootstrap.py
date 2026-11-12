from pathlib import Path
import subprocess,json,os,time,shutil,re,sys,hashlib
import record_run
P=Path('/home/patrick/work/s3a')
def env():return record_run.session_environment()[0]
def shells():return subprocess.check_output(['pgrep','-u',str(os.getuid()),'-x','gnome-shell'],text=True).split()
def relogin(name):
 r=subprocess.run(['python3',str(P/'audit-apps.py')],capture_output=True,text=True);(P/(name+'-prelogout-apps.json')).write_text(r.stdout);assert r.returncode==0,'Patrick apps or incomplete inventory; logout refused'
 old=shells();subprocess.run(['sudo','-n','systemctl','restart','gdm'],check=True)
 for _ in range(60):
  try:
   now=shells()
   if now and set(now).isdisjoint(old):break
  except subprocess.CalledProcessError:pass
  time.sleep(1)
 else:raise RuntimeError('new GNOME session unavailable after GDM restart')
 time.sleep(8);e=env();subprocess.run(['gdbus','call','--session','-d','org.gnome.Shell','-o','/org/gnome/Shell','-m','org.freedesktop.DBus.Properties.Set','org.gnome.Shell','OverviewActive','<false>'],env=e,capture_output=True)
 subprocess.run(['systemctl','--user','restart','putgd-gnome-vnc.service'],env=e,check=True);time.sleep(2)
 subprocess.run(['gnome-extensions','enable','putgd@put.gd'],env=e,check=True);time.sleep(1)
 info=subprocess.check_output(['gnome-extensions','info','putgd@put.gd'],env=e,text=True);(P/(name+'-extension.txt')).write_text(info);assert 'ACTIVE' in info,info
 (P/(name+'-session.json')).write_text(json.dumps({'oldShellPids':old,'newShellPids':now,'extension':info},indent=2));print(name,info,flush=True)
relogin('nightly-loaded')
assert re.search(r'Version:\s*21\b',(P/'nightly-loaded-extension.txt').read_text()),'published nightly extension was not version21'
ci=P/'putgd-26.1112.4716~dev+g0311647141ff-1.fc44.x86_64.rpm';before=shells()
with (P/'ci-install.log').open('w') as log:r=subprocess.run(['sudo','-n','dnf','install','-y',str(ci)],stdout=log,stderr=subprocess.STDOUT)
assert r.returncode==0,r.returncode;assert shells()==before,'Shell changed while installing CI'
(P/'installed.json').write_text(json.dumps({'package':ci.name,'sha256':hashlib.sha256(ci.read_bytes()).hexdigest(),'build':json.loads(subprocess.check_output(['putgd-cli','--version-json']))},indent=2));(P/'packages-after.txt').write_bytes(subprocess.check_output(['rpm','-qa','--qf','%{NAME}\n']))
import pass2 as p
p.setup();out={'oldExtensionShellPids':before,'ciBuild':json.loads((P/'installed.json').read_text()),'capabilities':p.rpc('scroll.capabilities'),'beforeHistory':p.rpc('history.list',{'limit':200}),'requests':[]}
for method,args in [('action.invoke',{'action':'scroll'}),('scroll.prepare',{'rect':[100,200,960,600],'maxHeight':30000})]:
 try:
  value=p.rpc(method,args);out['requests'].append({'method':method,'unexpectedSuccess':value})
  if value.get('id'):
   try:p.rpc('scroll.cancel',{'id':value['id']})
   except Exception:pass
 except Exception as ex:out['requests'].append({'method':method,'refusal':str(ex)})
out['afterHistory']=p.rpc('history.list',{'limit':200});out['shellPidsAfterGuard']=shells();(P/'old-extension-guard.json').write_text(json.dumps(out,indent=2));print('old extension guard',json.dumps(out['requests']),flush=True)
try:p.rpc('ui.quit')
except Exception:pass
time.sleep(3);saved=P/'c17-private-before-relogin';saved.mkdir()
for n in ['c','d','s','cache','r','archive','env.json','identity.json','capabilities.json','rpc.jsonl','helper.log','resident.pid','resident.log']:
 if (P/n).exists():(P/n).rename(saved/n)
relogin('ci-loaded')
assert re.search(r'Version:\s*22\b',(P/'ci-loaded-extension.txt').read_text()),'CI extension was not version22'
p.setup();print('CI extension22 active, fresh private resident ready',flush=True)
