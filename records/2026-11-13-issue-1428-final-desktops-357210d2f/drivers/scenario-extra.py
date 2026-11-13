import json,os,sys,time,subprocess,hashlib,re
from pathlib import Path
FINAL='357210d2f1cb7b65f77166e34eb535d42e497fd0'
def extra(r):
 out=r.receipt['finalAcceptance']={'expectedCommit':FINAL,'quickRedact':{}};q=out['quickRedact'];base=Path(__file__).parent;observer=None;ident=None
 def frame(label):
  from rfb import RFB
  v=RFB(int(os.environ['PUTGD_MEASUREMENT_VNC_PORT']));v.frame();time.sleep(.25);v.frame();p=r.root/(label+'.png');v.screenshot(str(p));v.close();out.setdefault('frames',[]).append(p.name);return str(p)
 def children():
  found=[]
  for task in Path('/proc',str(r.resident_pid()),'task').glob('*/children'):
   for pid in task.read_text().split():
    try:
     args=Path('/proc',pid,'cmdline').read_bytes().split(b'\0')
     if b'--edit-image' in args and Path('/proc',pid,'comm').read_text().strip()=='putgd-ui':found.append(int(pid))
    except FileNotFoundError:pass
  return sorted(set(found))
 def stop_watch():
  if observer and observer.poll() is None:subprocess.run(['sudo','-n','kill',str(observer.pid)]);observer.wait(timeout=10)
 try:
  assert r.receipt['build']['gitCommit']==FINAL,r.receipt['build']
  expected='ALPHA BRAVO CHARLIE\nSYNTHETIC TEXT 1428\nhello@example.test'
  for t in r.receipt['triggers']:
   t['pasteMatchesExact']=t.get('paste')==expected;t['passed']=t.get('passed',False) and t['pasteMatchesExact']
  r.receipt['passed']=r.receipt['passed'] and all(t['passed'] for t in r.receipt['triggers'])
  out['smokePassed']=all(t['passed'] for t in r.receipt['triggers'])
  if os.environ.get('PUTGD_FINAL_LATENCY')=='1':
   import measure
   measure.extra(r)
  original=base/'text.png';src=r.root/'quick-source.png';src.write_bytes(original.read_bytes());q['source']={'file':str(src),'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'expectedLines':['ALPHA BRAVO CHARLIE','SYNTHETIC TEXT 1428','hello@example.test']}
  q['open']=r.cli('editor.open',{'source':'file','path':str(src)})['result'];ident=q['open']['operationId']
  def ready():
   v=r.cli('editor.inspect',{'id':ident},check=False)
   return v['result'] if v.get('ok') and v['result'].get('phase')=='editing' else None
  q['before']=r.wait(ready,'visible editor ready',35);assert q['before'].get('shapes')==[],q['before']
  pids=r.wait(lambda:children(),'owned editor process',15);assert len(pids)==1,pids;pid=pids[0];q['editorPid']=pid;q['editorStartTicks']=Path('/proc',str(pid),'stat').read_text().rsplit(') ',1)[1].split()[19]
  q['raise']=r.cli('editor.raise',{'id':ident},check=False)
  # Production compositor operations target this exact owned editor PID only.
  if r.x11:
   windows=subprocess.run(['xdotool','search','--pid',str(pid)],env=r.env,capture_output=True,text=True).stdout.split()
   if windows:q['x11Raise']=subprocess.run(['xdotool','windowactivate','--sync',windows[-1]],env=r.env,capture_output=True,text=True).returncode
  elif 'KDE' in r.env.get('XDG_CURRENT_DESKTOP',''):
   def bus(*a):return subprocess.run(['dbus-send','--session','--print-reply','--dest=org.kde.KWin',*a],env=r.env,capture_output=True,text=True)
   name='b1428-final-editor-'+r.root.name;script=r.root/'raise-owned-editor.js';script.write_text('for (const w of workspace.windowList()) { if (Number(w.pid) === '+str(pid)+') workspace.activeWindow=w; }')
   load=bus('/Scripting','org.kde.kwin.Scripting.loadScript','string:'+str(script),'string:'+name);m=re.search(r'int32 (\d+)',load.stdout);q['kwinRaise']={'loaded':bool(m)}
   if m:
    a=bus('/Scripting/Script'+m.group(1),'org.kde.kwin.Script.run')
    if a.returncode:a=bus('/Scripting/'+m.group(1),'org.kde.kwin.Script.run')
    q['kwinRaise']['code']=a.returncode;q['kwinRaise']['unload']=bus('/Scripting','org.kde.kwin.Scripting.unloadScript','string:'+name).returncode
  elif 'Hyprland' in r.env.get('XDG_CURRENT_DESKTOP',''):
   v=subprocess.run(['hyprctl','clients','-j'],env=r.env,capture_output=True,text=True);clients=json.loads(v.stdout)
   for c in clients:
    if c.get('pid')==pid:q['hyprRaise']=subprocess.run(['hyprctl','dispatch','focuswindow','address:'+c['address']],env=r.env,capture_output=True,text=True).returncode;break
  time.sleep(1);frame('editor-before-quick')
  print('EDITOR-READY '+str(r.root),flush=True)
  # The controlling tester observes these frames. Optional real key/pointer
  # commands use the same already-owned input channel, never a second client.
  deadline=time.monotonic()+900;n=0
  while not (r.root/'editor-go.txt').exists():
   cmd=r.root/'editor-input.json'
   if cmd.exists():
    c=json.loads(cmd.read_text());cmd.unlink();out.setdefault('focusInputs',[]).append(c)
    if 'keys' in c:r.input.chord(c['keys'])
    elif 'click' in c:r.input.click(*c['click'])
    else:raise RuntimeError('Unknown editor focus input')
    time.sleep(1);n+=1;frame('editor-focus-'+str(n));print('EDITOR-FOCUS '+str(n)+' '+str(r.root),flush=True)
   if time.monotonic()>deadline:raise RuntimeError('Editor observation timeout')
   time.sleep(.2)
  q['visualBefore']=(r.root/'editor-go.txt').read_text()
  events=r.root/'quick-helper-events.jsonl';observer=subprocess.Popen(['sudo','-n','python3','-I',str(base/'lifecycle_watch.py'),str(events),'putgd-ocr',str(pid)]);r.wait(events.exists,'Quick redact lifecycle observer');time.sleep(.1)
  q['apply']=r.cli('editor.apply',{'id':ident,'commands':[{'op':'redactText','categories':['email']}]},check=False)
  q['after']=r.cli('editor.inspect',{'id':ident},check=False)
  q['save']=r.cli('editor.saveCopy',{'id':ident,'path':str(r.root/'quick-email.png')},check=False)
  time.sleep(.7);stop_watch();q['helperEvents']=[json.loads(x) for x in events.read_text().splitlines() if x.strip()]
  shapes=q.get('after',{}).get('result',{}).get('shapes',[]);q['exactlyOneEmailMark']=bool(q['apply'].get('ok')) and len(shapes)==1 and shapes[0].get('kind')=='redact' and len(q['apply'].get('result',{}).get('created',[]))==1 and q['apply'].get('result',{}).get('counts',{}).get('email')==1
  q['emailRowOnly']=q['exactlyOneEmailMark'] and shapes[0]['rect'][1]>130 and shapes[0]['rect'][1]+shapes[0]['rect'][3]<210
  sp={(e['pid'],str(e['startTicks'])) for e in q['helperEvents'] if e.get('event')=='spawn'};ex={(e['pid'],str(e['startTicks'])) for e in q['helperEvents'] if e.get('event')=='exit' and e.get('exitCode')==0};q['oneHelperExit0']=len(sp)==1 and sp==ex
  frame('editor-after-quick');print('QUICK-READY '+str(r.root)+' '+json.dumps({k:q[k] for k in ['exactlyOneEmailMark','emailRowOnly','oneHelperExit0']}),flush=True)
  r.wait(lambda:(r.root/'verification.json').exists(),'tester visual and PNG verification',900);q['externalVerification']=json.loads((r.root/'verification.json').read_text());q['passed']=q['exactlyOneEmailMark'] and q['emailRowOnly'] and q['oneHelperExit0'] and q['save'].get('ok',False) and q['externalVerification'].get('passed',False)
  out['passed']=q['passed'];r.receipt['passed']=r.receipt['passed'] and out['passed']
 except Exception as e:
  out['error']=str(e);out['passed']=False;r.receipt['passed']=False;print('FINAL-ERROR '+str(r.root)+' '+str(e),flush=True)
 finally:
  stop_watch()
  if ident:
   try:q['cancel']=r.cli('editor.cancel',{'id':ident},check=False)
   except Exception as e:q['cancelError']=str(e)
  print('FINAL-RESULT '+str(r.root)+' '+json.dumps({'passed':out.get('passed'),'error':out.get('error')}),flush=True)
