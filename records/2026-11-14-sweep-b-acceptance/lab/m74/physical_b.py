#!/usr/bin/env python3
import json,pathlib,sys,time,subprocess,os,hashlib
import record_acceptance as setup
r=setup.r

def flow(self):
 b=r.Build(*self.args.build[0].split('=',1),self.run);fixture=None;active=None;editor=None;player=None;report=[];out=self.run/'fixture';control_id=0
 def row(name,passed=True,**v):report.append({'row':name,'passed':passed,**v});(self.run/'physical.json').write_text(json.dumps(report,indent=2))
 def call(m,p=None):return self.cli(b,m,p)
 def xd(*a):return subprocess.check_output(['xdotool',*map(str,a)],env=self.env,text=True,timeout=5).strip()
 def wait_op(op):
  for _ in range(200):
   v=call('operation.inspect',{'id':op})
   if v['state'] in ('completed','failed','cancelled','partial'):return v
   time.sleep(.1)
  raise RuntimeError('operation deadline')
 def record_wait(rid,states):return self.wait_state(b,rid,states,100)
 def control(**v):
  nonlocal control_id
  control_id+=1;v['id']=control_id;t=out/'control.tmp';t.write_text(json.dumps(v));t.replace(out/'control.json')
  for _ in range(40):
   if (out/'control-ack.json').exists() and json.loads((out/'control-ack.json').read_text()).get('id')==control_id:return
   time.sleep(.05)
  raise RuntimeError('Fixture control deadline')
 def focus():
  if self.env.get('XDG_SESSION_TYPE')=='x11':
   identity=xd('search','--name','^put.gd independent GTK clipboard fixture$').splitlines()[-1];xd('windowactivate','--sync',identity)
  else:
   script=self.run/'raise.js';script.write_text('const w=workspace.windowList().find(w=>w.caption==="put.gd independent GTK clipboard fixture");if(w){w.minimized=false;workspace.activeWindow=w;}');name='sweep-b-raise';ident=subprocess.check_output(['qdbus6','org.kde.KWin','/Scripting','org.kde.kwin.Scripting.loadScript',str(script),name],env=self.env,text=True,timeout=5).strip()
   subprocess.run(['qdbus6','org.kde.KWin','/Scripting/Script'+ident,'org.kde.kwin.Script.run'],env=self.env,check=True,stdout=subprocess.DEVNULL);subprocess.run(['qdbus6','org.kde.KWin','/Scripting','org.kde.kwin.Scripting.unloadScript',name],env=self.env,check=True,stdout=subprocess.DEVNULL)
  
  if self.env.get('XDG_SESSION_TYPE')=='x11':xd('mousemove',1900,900)
  time.sleep(.3);p=self.run/'frames/fixture-oracle.png';self.desktop_frame(p)
  import lab
  from PIL import Image
  image=Image.open(p);ppm=self.run/'frames/fixture-oracle.ppm';image.save(ppm);found=lab.locate_fixture_paint(ppm);assert found,'Native fixture not visible';return found
 def drag(x,y,size):
  xd('mousemove',x,y);xd('mousedown',1);xd('mousemove','--sync',x+size,y+size);time.sleep(.1);xd('mouseup',1)
 def process_tree(stage):
  root=self.resident.pid;allp={}
  for p in pathlib.Path('/proc').iterdir():
   if not p.name.isdecimal():continue
   try:
    st=(p/'stat').read_text().rsplit(')',1)[1].split();allp[int(p.name)]={'pid':int(p.name),'parent':int(st[1]),'startTicks':int(st[19]),'comm':(p/'comm').read_text().strip(),'exe':os.readlink(p/'exe')}
   except OSError:pass
  ids={root}
  while True:
   new={p for p,v in allp.items() if v['parent'] in ids}
   if new<=ids:break
   ids|=new
  offered=call('recording.windows') if self.env.get('XDG_SESSION_TYPE')!='x11' else {'windows':[], 'notRun':'X11 has no recording window list; process tree only'};external=[w for w in offered['windows'] if 'independent GTK' in w.get('title','')];own=[w for w in offered['windows'] if w.get('title') in ('put.gd','Edit image','Review recording')]
  exclusion=None
  if self.env.get('XDG_SESSION_TYPE')=='x11':
   helpers=[v for k,v in allp.items() if k in ids and v['comm']==('putgd-record' if 'bar' in stage or 'review' in stage else 'putgd-ui')]
   for helper in helpers:
    candidates=xd('search','--onlyvisible','--pid',helper['pid']).splitlines()
    for window in candidates:
     title=xd('getwindowname',window)
     if 'editor' in stage and not title.startswith('Edit image'):continue
     if 'review' in stage and title!='Review recording':continue
     try:xd('windowactivate',window)
     except Exception:continue
     time.sleep(.2);focused=xd('getactivewindow')
     if focused!=window:continue
     raw=subprocess.run([b.cli,'action.invoke',json.dumps({'action':'window'})],env=self.env,text=True,capture_output=True);exclusion={'focusedWindow':window,'title':title,'ownerPid':helper['pid'],'reply':json.loads(raw.stdout)}
     value=exclusion['reply'];result=wait_op(value['result']['operationId']) if value.get('ok') else value
     exclusion['outcome']=result;code=(result.get('error') or {}).get('code')
     assert code=='capture_target',exclusion;break
    if exclusion:break
  if self.env.get('XDG_SESSION_TYPE')=='x11' and 'bar' not in stage:assert exclusion,'Owned window could not be focused: '+stage
  tree={'stage':stage,'exclusion':exclusion,'resident':root,'processes':[allp[p] for p in sorted(ids) if p in allp],'offered':offered};(self.run/(stage+'-processes.json')).write_text(json.dumps(tree,indent=2));assert (external and not own) or self.env.get('XDG_SESSION_TYPE')=='x11',tree
  self.desktop_frame(self.run/'frames'/(stage+'.png'));return tree
 def screenshot1():
  p=focus();op=call('action.invoke',{'action':'region'})['operationId'];time.sleep(1);drag(p['x']+50,p['y']+50,1);v=wait_op(op)
  from PIL import Image
  path=v['items'][0]['local']['path'];im=Image.open(path);assert im.size==(1,1),(im.size,v);row('8-screenshot-1px',operation=v,size=list(im.size));self.desktop_frame(self.run/'frames/8-screenshot-after.png')
 def selection(size=None,escape=False):
  nonlocal active
  p=focus();active=call('recording.prepare',{'target':{'kind':'region'},'format':'mp4','audio':{'system':False}})['recordingId']
  for _ in range(100):
   state=call('recording.inspect',{'id':active})
   if state.get('selecting'):break
   time.sleep(.1)
  time.sleep(.3)
  if escape:xd('key','Escape')
  else:drag(p['x']+100,p['y']+100,size)
  op=wait_op(active) if escape or size<4 else record_wait(active,('ready',))
  expected=op['state']=='cancelled' if escape or size<4 else op['state']=='ready'
  row('9-select-escape' if escape else '8-recording-drag-'+str(size),expected,operation=op)
  if op['state']=='ready':call('recording.cancel',{'id':active})
  active=None;self.desktop_frame(self.run/'frames'/('selection-escape.png' if escape else 'selection-'+str(size)+'.png'))
 def clean_record():
  nonlocal active
  if active:
   try:call('recording.cancel',{'id':active})
   except Exception:pass
   active=None
 def record(moving,escape_test=False):
  nonlocal active,player
  control(motion=False);p=focus();target={'kind':'monitor'};active=call('recording.prepare',{'target':target,'format':'mp4','audio':{'system':False},'clickHighlights':moving and self.env.get('XDG_SESSION_TYPE')=='x11'})['recordingId'];rid=active;ready=record_wait(rid,('ready',));process_tree('11-bar' if moving else 'control-bar');call('recording.overlay',{'id':rid,'visible':False});control(motion=moving);call('recording.start',{'id':rid});time.sleep(1)
  click_info=None
  if moving:
   if self.env.get('XDG_SESSION_TYPE')=='x11':
    x=p['x']+190;y=p['y']+365;xd('mousemove',x,y);time.sleep(.7);before=call('recording.inspect',{'id':rid});xd('click',1);time.sleep(.6);click_info={'x':x,'y':y,'beforePress':before,'reaction':json.loads((out/'clicks.json').read_text())};assert click_info['reaction']['count']>=1
   else:
    from rfb import RFB
    vnc=RFB(5900)
    try:
     for n in range(5):vnc.pointer(p['x']+40+n*35,p['y']+80);time.sleep(.25)
    finally:vnc.close()
  if escape_test:
   xd('key','Escape');time.sleep(.8);after=call('recording.inspect',{'id':rid});row('9-recording-escape',after['state']=='reviewing',afterEscape=after,observed=after['state'])
  else:after=call('recording.inspect',{'id':rid})
  if after['state']=='recording':call('recording.pause',{'id':rid});time.sleep(.3);call('recording.resume',{'id':rid});time.sleep(1);call('recording.stop',{'id':rid})
  review=record_wait(rid,('reviewing',));process_tree('11-review' if moving else 'control-review');path=self.run/'out'/('moving.mp4' if moving else 'frozen.mp4');call('recording.saveCopy',{'id':rid,'path':str(path)});exported=record_wait(rid,('reviewing',));motion=self.motion(path)
  result={'ready':ready,'review':review,'exported':exported,'motion':motion,'path':str(path),'click':click_info}
  if click_info:
   progress=click_info['beforePress'].get('progress',{});us=progress.get('durationUs',click_info['beforePress'].get('durationUs',0));arg='%d,%d,%d,%d'%(max(0,int(us/1000)-100),int(us/1000)+1200,click_info['x'],click_info['y']);probe=self.helper('--click-check',path,arg);result['clickCheck']=json.loads(probe.stdout);row('9-click-highlight',any(w.get('seen') for w in result['clickCheck'].get('watches',[])),check=result['clickCheck'],reaction=click_info['reaction'])
  row('10-export-moving' if moving else '10-frozen-control',True,**result);clean_record();control(motion=False)
  if moving:
   player=subprocess.Popen([sys.executable,str(pathlib.Path(__file__).parent/'gst_player.py'),str(path),str(self.run/'playback.json')],env=self.env,stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=open(self.run/'logs/player.log','w'))
   time.sleep(3);self.desktop_frame(self.run/'frames/10-export-playback.png');samples=json.loads((self.run/'playback.json').read_text());okay=any(x['timestampUs']>500000 and not x['error'] for x in samples);row('10-playback',okay,samples=samples);player.terminate();player.wait(10);player=None
  return motion
 try:
  self.start_resident(b);time.sleep(3)
  if self.env.get('XDG_SESSION_TYPE')=='x11':
   result=subprocess.run(['gdbus','call','--session','--dest','org.Cinnamon','--object-path','/org/Cinnamon','--method','org.Cinnamon.Eval','if(imports.ui.main.messageTray._notification?.title==="put.gd") imports.ui.main.messageTray._hideNotificationCompleted();'],env=self.env,capture_output=True,text=True);(self.run/'notification-dismiss.json').write_text(json.dumps({'returncode':result.returncode,'output':result.stdout}));time.sleep(.5)
  try:self.open_cover()
  except Exception:
   self.desktop_frame(self.run/'frames/cover-guard-failure.png');raise
  fixture=subprocess.Popen([sys.executable,str(pathlib.Path(__file__).parent/'guest_fixture.py'),str(out)],env=self.env,stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=open(self.run/'logs/fixture.log','w'));time.sleep(2)
  caps=call('recording.capabilities');row('capabilities',capabilities=caps)
  settings=call('settings.get');call('settings.patch',{'patch':{'actions':{a:{'destination':'local','profileId':None} for a in ('region','desktop','window','clipboard','edit','record')}},'expectedRevision':settings['metadata']['observedRevision']})
  if self.env.get('XDG_SESSION_TYPE')=='x11':
   for name,fn in [('8-1px',screenshot1),('8-small',lambda:selection(3)),('8-four',lambda:selection(4)),('9-esc-select',lambda:selection(escape=True))]:
    try:fn()
    except Exception as e:row(name,False,error=str(e));clean_record()
  else:
   p=focus();op=call('action.invoke',{'action':'region'})['operationId'];time.sleep(1)
   from rfb import RFB
   vnc=RFB(5900)
   try:vnc.drag(p['x']+10,p['y']+10,p['x']+310,p['y']+210)
   finally:vnc.close()
   v=wait_op(op);row('12-region',v['state']=='completed',operation=v)
  if self.env.get('XDG_SESSION_TYPE')=='x11':
   p=focus();op=call('action.invoke',{'action':'window'})['operationId'];v=wait_op(op);assert v['state']=='completed',v;row('11-external-window',operation=v)
  frozen=record(False);moving=record(True,self.env.get('XDG_SESSION_TYPE')=='x11');row('12-monitor-motion' if self.env.get('XDG_SESSION_TYPE')=='wayland' else '10-motion-vs-control',moving>frozen+.05,motion=moving,frozenControl=frozen)
  for view in ('settings','history'):
   call('ui.show',{'view':view});time.sleep(1);row('11-'+view,tree=process_tree('11-'+view))
  editor=call('editor.open',{'source':'file','path':str(out/'text.png')})['operationId'];time.sleep(1);row('11-editor',tree=process_tree('11-editor'));call('editor.cancel',{'id':editor});editor=None
 except Exception as e:row('driver-error',False,error=str(e));raise
 finally:
  clean_record()
  if editor:
   try:call('editor.cancel',{'id':editor})
   except Exception:pass
  if player:player.terminate();player.wait(10)
  if fixture:
   row('fixture-process-before-cleanup',fixture.poll() is None,pid=fixture.pid,returncode=fixture.poll());fixture.terminate();fixture.wait(10)
  self.stop_resident(b);self.close_cover()
 return 0
r.Driver.main=flow
sys.exit(r.main())
