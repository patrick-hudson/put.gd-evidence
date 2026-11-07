import os,sys,pathlib,subprocess,json,time,uuid,hashlib
sys.path.insert(0,str(pathlib.Path.home()/'nd'))
from tools.lab import provision_live_credentials as bridge
from tools.lab.surface_driver.fixtures.live_outcomes import key_set_two
os.umask(0o077)
p=pathlib.Path('/tmp/u1245b');p.mkdir(exist_ok=True);runtime=p/'rt';runtime.mkdir(exist_ok=True)
app=pathlib.Path.home()/'c1245b/debian/app/usr';bin=app/'bin'
env=dict(os.environ,QT_QPA_PLATFORM='offscreen',XDG_RUNTIME_DIR=str(runtime),XDG_CONFIG_HOME=str(p/'config'),XDG_STATE_HOME=str(p/'state'),XDG_CACHE_HOME=str(p/'cache'),DBUS_SESSION_BUS_ADDRESS='unix:path=/run/user/1000/bus',LD_LIBRARY_PATH=str(app/'lib/x86_64-linux-gnu')+':'+str(app/'lib'))
socket=str(runtime/'putgd/session.sock');assert len(socket.encode())<=107
out=pathlib.Path.home()/'c1245b/live2';out.mkdir(exist_ok=True)
(out/'socket.json').write_text(json.dumps({'path':socket,'utf8Bytes':len(socket.encode())}))
log=(out/'resident.log').open('a');proc=subprocess.Popen([str(bin/'putgd'),'--background'],env=env,stdout=log,stderr=log)
(out/'pid.json').write_text(json.dumps({'pid':proc.pid,'app':str(bin/'putgd')}))
def cli(method,params={}):
 r=subprocess.run([str(bin/'putgd-cli'),'--socket',socket,method,json.dumps(params)],env=env,capture_output=True,text=True,timeout=150)
 try:d=json.loads(r.stdout)
 except:raise RuntimeError('cli_bad_reply_'+method)
 if not d.get('ok'):raise RuntimeError('cli_'+method+'_'+str((d.get('error') or {}).get('code')))
 return d['result']
def wait(method,params,done,seconds=600):
 end=time.monotonic()+seconds
 while time.monotonic()<end:
  d=cli(method,params)
  if done(d):return d
  time.sleep(1)
 raise RuntimeError('timeout_'+method)

result=json.loads((out/'result.json').read_text())
try:
 for i in range(30):
  if pathlib.Path(socket).exists():break
  time.sleep(1)
 time.sleep(3)
 d=cli('delete.inspect',{'id':result['deleteOperation']['deleteOperationId']})
 (out/'deletion-recovered.json').write_text(json.dumps(d,indent=2))
 detail=cli('history.detail',{'id':result['history']['id']})
 result['remoteStatus']=detail.get('remoteStatus');result['recoveredDeletion']=d
 if detail.get('remoteStatus') in ('removed','already_missing'):
  result['status']='PASS';result['controllerCorrection']='delete response field is deleteOperationId; inspected existing deletion, no second delete'
  result.pop('reason',None)
  os.environ['DBUS_SESSION_BUS_ADDRESS']=env['DBUS_SESSION_BUS_ADDRESS']
  bridge.host_call(str(pathlib.Path.home()/'putgd-lab/proton/bridge/putgd-lab-secret-bridge'),'s3',dict(op='delete',reference=result['credentialReference']))
  result['credentialRemoved']=True
 (out/'result.json').write_text(json.dumps(result,indent=2))
 print(json.dumps({'status':result['status'],'remoteStatus':result['remoteStatus']}))
finally:
 cli('ui.quit');proc.wait(timeout=25)
