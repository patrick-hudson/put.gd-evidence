import json,os,time,subprocess as sp
from pathlib import Path
root=Path('/tmp/m13');root.mkdir(mode=0o700)
base=os.environ.copy()
for d in Path('/proc').iterdir():
 try:
  if (d/'comm').read_text().strip()=='cinnamon':
   env=dict(x.split('=',1) for x in (d/'environ').read_bytes().decode().split('\0') if '=' in x)
   for k in ('DISPLAY','XAUTHORITY','DBUS_SESSION_BUS_ADDRESS','XDG_CURRENT_DESKTOP','XDG_SESSION_TYPE'): 
    if k in env:base[k]=env[k]
   break
 except (OSError,UnicodeError):pass
base.update(QT_QPA_PLATFORM='xcb',XDG_SESSION_TYPE='x11',XDG_CURRENT_DESKTOP='X-Cinnamon')
base.setdefault('DISPLAY',':0');base.setdefault('DBUS_SESSION_BUS_ADDRESS','unix:path=/run/user/1000/bus')
def run(args,env=base,timeout=20):
 return sp.run(list(map(str,args)),env=env,capture_output=True,text=True,timeout=timeout)
def wait(read,pred,seconds=15):
 end=time.monotonic()+seconds
 while time.monotonic()<end:
  value=read()
  if pred(value):return value
  time.sleep(.05)
 raise RuntimeError('condition timed out')
for label in ('fixed','nightly'):
 out=root/label;out.mkdir(mode=0o700);env=base.copy()
 for key,name in [('XDG_CONFIG_HOME','config'),('XDG_DATA_HOME','data'),('XDG_STATE_HOME','state'),('XDG_CACHE_HOME','cache'),('XDG_RUNTIME_DIR','rt')]:
  path=out/name;path.mkdir(mode=0o700);env[key]=str(path)
 sock=out/'rt/putgd/session.sock';assert len(str(sock).encode())<=107
 binary=Path('/tmp/m1380-'+label)
 resident=sp.Popen([str(binary/'putgd'),'--background'],env=env,stdout=open(out/'resident.log','w'),stderr=sp.STDOUT)
 (out/'resident.pid').write_text(str(resident.pid));cover=None
 def cli(method,params={}):
  reply=run([binary/'putgd-cli',method,json.dumps(params)],env);data=json.loads(reply.stdout)
  if not data.get('ok'):raise RuntimeError(method+':'+str(data.get('error')))
  return data['result']
 try:
  wait(lambda:sock.exists(),bool)
  (out/'capabilities.json').write_text(json.dumps(cli('capabilities')))
  settings=cli('settings.get');patch={'profiles':[],'actions':{k:{'destination':'local','profileId':None,'shortcut':'Ctrl+Shift+F12' if k=='region' else ''} for k in ('region','window','desktop','clipboard','edit')},'archive':{'keepUploads':True,'root':str(out/'output')},'preferences':{'notifications':False,'updates':{'check':False},'regionSelectionMode':'live'}}
  cli('settings.patch',{'patch':patch,'expectedRevision':settings['metadata']['observedRevision']})
  (out/'accepted-settings.json').write_text(json.dumps(cli('settings.get')))
  if label=='fixed':
   cover=sp.Popen(['/tmp/pg-cover'],env=env);(out/'cover.pid').write_text(str(cover.pid));time.sleep(.6)
   assert run(['xdotool','key','ctrl+shift+F12'],env).returncode==0
   def helper():
    for pid in Path(f'/proc/{resident.pid}/task/{resident.pid}/children').read_text().split():
     try:
      if Path(f'/proc/{pid}/exe').resolve()==binary/'putgd-capture':return int(pid)
     except OSError:pass
    return None
   hp=wait(helper,bool);time.sleep(.3)
   ids=run(['xdotool','search','--pid',hp],env).stdout.split();details=[]
   for wid in ids:
    details.append(run(['xprop','-id',wid,'_NET_WM_PID','WM_CLASS'],env).stdout+run(['xwininfo','-id',wid],env).stdout)
   text='\n'.join(details);(out/'helper-windows.txt').write_text(f'helper PID {hp}\n'+text)
   assert 'IsUnMapped' in text and 'IsViewable' in text
   run(['import','-window','root',out/'selector.png'],env)
   run(['xdotool','mousemove','400','300','mousedown','1','mousemove','800','550'],env);time.sleep(.2)
   run(['import','-window','root',out/'drag.png'],env)
   run(['xdotool','mouseup','1'],env)
   files=wait(lambda:list((out/'output').rglob('*.png')),bool)
   (out/'capture-files.json').write_text(json.dumps([str(p) for p in files]))
   before=len(files);run(['xdotool','key','ctrl+shift+F12'],env);wait(helper,bool);time.sleep(.2)
   run(['xdotool','key','Escape'],env);wait(helper,lambda x:x is None);time.sleep(.2)
   assert len(list((out/'output').rglob('*.png')))==before
   (out/'functional.json').write_text(json.dumps({'shortcutMaps':True,'dragCaptures':True,'escapeCancelsWithoutFile':True,'helperPid':hp,'unmappedWarmupVerified':True}))
   cover.terminate();cover.wait(timeout=5);cover=None
  result=run(['/tmp/pg-map-probe','--resident-pid',resident.pid,'--capture-helper',binary/'putgd-capture','--live-outline','--output',out/'latency.json'],env,timeout=240)
  (out/'probe.log').write_text(result.stdout+result.stderr)
  data=json.loads((out/'latency.json').read_text());assert not data['error'],data['error'];assert len(data['samples'])==30
  print(label,'native/probe complete',flush=True)
 finally:
  if cover and cover.poll() is None:cover.terminate();cover.wait(timeout=5)
  if resident.poll() is None:
   try:cli('ui.quit');resident.wait(timeout=10)
   except Exception:resident.terminate();resident.wait(timeout=5)
