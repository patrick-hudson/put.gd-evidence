#!/usr/bin/env python3
"""Round C: real X11 scroll Escape delivery and window-manager bar activation."""
import json,pathlib,sys,time,subprocess,os,re,traceback
import record_acceptance as setup
r=setup.r
def flow(self):
 b=r.Build(*self.args.build[0].split('=',1),self.run);fixture=None;sid=None;rid=None;rows=[];serial=0;out=self.run/'fixture';out.mkdir()
 def save(name,data): (self.run/name).write_text(json.dumps(data,indent=2))
 def row(name,passed,**data):rows.append({'row':name,'passed':passed,**data});save('rows.json',rows)
 def call(m,p=None):return self.cli(b,m,p)
 def command(args,timeout=6):
  try:
   p=subprocess.run(args,env=self.env,text=True,capture_output=True,timeout=timeout);return {'argv':list(map(str,args)),'exitCode':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
  except subprocess.TimeoutExpired:return {'argv':list(map(str,args)),'timeout':timeout}
 def xd(*args):
  j=command(['xdotool',*map(str,args)]);assert j.get('exitCode')==0,j;return j['stdout'].strip()
 def active():
  p=command(['xprop','-root','_NET_ACTIVE_WINDOW']);q=re.search(r'0x[0-9a-fA-F]+',p.get('stdout',''));return {'netActiveWindow':int(q[0],16) if q else None,'property':p,'inputFocus':command(['xdotool','getwindowfocus'])}
 def focus(name):
  title='Sweep C scrolling page' if name=='page' else 'Sweep C other key receiver';wid=int(xd('search','--onlyvisible','--name','^'+title+'$').splitlines()[-1]);xd('windowactivate','--sync',wid);time.sleep(.12);a=active();assert a['netActiveWindow']==wid,(name,a);return wid,a
 def fixture_state():return json.loads((out/'state.json').read_text())
 def events():return [json.loads(x) for x in (out/'events.jsonl').read_text().splitlines()] if (out/'events.jsonl').exists() else []
 def wait_operation(ident):
  for _ in range(160):
   v=call('operation.inspect',{'id':ident})
   if v['state'] in ('completed','partial','failed','cancelled'):return v
   time.sleep(.05)
  raise RuntimeError('operation did not finish')
 def reset(total):
  nonlocal serial
  serial+=1;j={'serial':serial,'total':total};p=out/'control.tmp';p.write_text(json.dumps(j));p.replace(out/'control.json')
  for _ in range(80):
   if any(e.get('serial')==serial for e in events()):break
   time.sleep(.05)
  else:raise RuntimeError('fixture reset not acknowledged')
  assert fixture_state()['position']==0
 def stop_scroll():
  nonlocal sid
  if sid:
   try:call('scroll.cancel',{'id':sid})
   except Exception:pass
   sid=None
 def scroll(name,escape=None):
  nonlocal sid
  reset(12000 if escape else 5000);focus('page');g=json.loads((out/'geometry.json').read_text());rect=[g['x'],g['y'],g['width'],g['height']]
  sid=call('scroll.prepare',{'rect':rect,'maxHeight':20000})['id'];call('scroll.start',{'id':sid});history=[]
  deadline=time.monotonic()+120
  if escape:
   while time.monotonic()<deadline:
    v=call('scroll.inspect',{'id':sid});history.append({'monotonic':time.monotonic(),'view':v})
    if v['state'] not in ('capturing','ready','preparing','finishing'):raise RuntimeError('Ended before Escape: '+json.dumps(v))
    if v['state']=='capturing' and fixture_state()['position']>=400:break
    time.sleep(.05)
   else:raise RuntimeError('No scrolling observed before Escape')
   wid,a=focus(escape);self.desktop_frame(self.run/'frames'/(name+'-before-escape.png'));a=active();assert a['netActiveWindow']==wid
   sent=time.monotonic();key=command(['xdotool','key','Escape']);assert key['exitCode']==0
  else:sent=None;a=None;key=None
  while time.monotonic()<deadline:
   v=call('scroll.inspect',{'id':sid});history.append({'monotonic':time.monotonic(),'view':v})
   if v['state'] in ('done','failed','cancelled'):break
   time.sleep(.05)
  else:raise RuntimeError('scroll did not end')
  terminal=time.monotonic();at_terminal=fixture_state();self.desktop_frame(self.run/'frames'/(name+'-finished.png'));time.sleep(3);after=fixture_state();self.desktop_frame(self.run/'frames'/(name+'-after-quiet.png'))
  ev=events();keys=[e for e in ev if sent is not None and e['monotonic']>=sent and e['kind']=='key-press' and e['key']=='Escape' and e['window']==escape]
  late=[e for e in ev if e['kind']=='wheel' and e['monotonic']>terminal]
  expected='stopped' if escape else 'end_of_content';passed=v['state']=='done' and v.get('endReason')==expected and not late and at_terminal==after
  if escape:passed=passed and bool(keys) and terminal-sent<5 and v.get('truncated') is True
  else:passed=passed and v.get('truncated') is False
  op=wait_operation(sid);row(name,passed,view=v,operation=op,escapeSentMonotonic=sent,terminalMonotonic=terminal,stopLatencySeconds=terminal-sent if sent else None,activeBeforeEscape=a,keyCommand=key,focusedApplicationEscapeEvents=keys,atTerminal=at_terminal,afterThreeSeconds=after,wheelEventsAfterTerminal=late,inspections=history);sid=None
 def tree():
  allp={}
  for p in pathlib.Path('/proc').iterdir():
   if not p.name.isdecimal():continue
   try:
    s=(p/'stat').read_text().rsplit(')',1)[1].split();allp[int(p.name)]={'pid':int(p.name),'parent':int(s[1]),'startTicks':int(s[19]),'comm':(p/'comm').read_text().strip(),'exe':os.readlink(p/'exe')}
   except OSError:pass
  ids={self.resident.pid}
  while True:
   new={k for k,p in allp.items() if p['parent'] in ids}
   if new<=ids:break
   ids|=new
  return [allp[k] for k in sorted(ids) if k in allp]
 def window(title):
  for _ in range(80):
   j=command(['xdotool','search','--onlyvisible','--name','^'+title+'$'])
   if j.get('exitCode')==0:return int(j['stdout'].splitlines()[-1])
   time.sleep(.1)
  raise RuntimeError('Window not visible: '+title)
 def attributes(wid):
  return {'id':wid,'xwininfo':command(['xwininfo','-id',str(wid),'-all']),'properties':command(['xprop','-id',str(wid),'_NET_WM_PID','_NET_WM_WINDOW_TYPE','WM_HINTS','WM_CLASS','WM_NAME']),'processTree':tree()}
 def bar():
  nonlocal rid
  focus('page');rid=call('recording.prepare',{'target':{'kind':'monitor'},'format':'mp4','audio':{'system':False}})['recordingId'];self.wait_state(b,rid,('ready',),90)
  wid=window('put.gd recording controls');before=attributes(wid);save('bar-attributes.json',before);attempts=[]
  geom=xd('getwindowgeometry','--shell',wid);fields=dict(line.split('=',1) for line in geom.splitlines() if '=' in line)
  for method in ('xdotool','wmctrl','click'):
   focus('page');pre=active()
   if method=='xdotool':cmd=command(['xdotool','windowactivate',str(wid)])
   elif method=='wmctrl':cmd=command(['wmctrl','-ia',hex(wid)])
   else:cmd=command(['xdotool','mousemove',str(int(fields['X'])+8),str(int(fields['Y'])+int(fields['HEIGHT'])//2),'click','1'])
   time.sleep(.4);post=active();probe=None
   if post['netActiveWindow']==wid:
    raw=command([str(b.cli),'action.invoke',json.dumps({'action':'window'})]);reply=json.loads(raw.get('stdout','{}'));probe={'reply':reply}
    if reply.get('ok'):probe['operation']=wait_operation(reply['result']['operationId'])
   attempts.append({'method':method,'before':pre,'command':cmd,'after':post,'captureWindowProbe':probe});self.desktop_frame(self.run/'frames'/('bar-'+method+'.png'))
  became_active=any(a['after']['netActiveWindow']==wid for a in attempts);save('bar-activation.json',attempts)
  call('recording.start',{'id':rid});time.sleep(1);call('recording.stop',{'id':rid});review_wid=window('Review recording');review=attributes(review_wid);save('review-attributes.json',review);self.desktop_frame(self.run/'frames/review.png')
  def owner(info):
   m=re.search(r'_NET_WM_PID\(CARDINAL\) = (\d+)',info['properties']['stdout']);return int(m[1]) if m else None
  bar_pid=owner(before);review_pid=owner(review);same=bar_pid is not None and bar_pid==review_pid
  if became_active:
   probes=[a['captureWindowProbe'] for a in attempts if a['after']['netActiveWindow']==wid];okay=all((p.get('operation',{}).get('error') or p['reply'].get('error') or {}).get('code')=='capture_target' for p in probes);classification='active and excluded'
  else:okay='Override Redirect State: yes' in before['xwininfo']['stdout'];classification='cannot occur through tested Cinnamon activation paths'
  row('2-bar-window-exclusion',okay and same,classification=classification,becameNetActive=became_active,barPid=bar_pid,reviewPid=review_pid,sameOwner=same,attempts=attempts,bar=before,review=review);call('recording.cancel',{'id':rid});rid=None
 try:
  self.start_resident(b);time.sleep(3)
  command(['gdbus','call','--session','--dest','org.Cinnamon','--object-path','/org/Cinnamon','--method','org.Cinnamon.Eval','if(imports.ui.main.messageTray._notification?.title==="put.gd") imports.ui.main.messageTray._hideNotificationCompleted();'])
  time.sleep(.5);self.open_cover();fixture=subprocess.Popen([sys.executable,str(pathlib.Path(__file__).parent/'scroll_keys.py'),str(out)],env=self.env,stdin=subprocess.DEVNULL,stdout=open(self.run/'logs/fixture.log','w'),stderr=subprocess.STDOUT)
  for _ in range(100):
   if (out/'geometry.json').exists():break
   if fixture.poll() is not None:raise RuntimeError('fixture exited')
   time.sleep(.1)
  self.desktop_frame(self.run/'frames/setup.png');caps=call('scroll.capabilities');save('scroll-capabilities.json',caps);assert caps['available'],caps
  settings=call('settings.get');call('settings.patch',{'expectedRevision':settings['metadata']['observedRevision'],'patch':{'actions':{'scroll':{'destination':'local','profileId':None}}}})
  for name,esc in [('1-escape-page','page'),('1-escape-other','other'),('1-end-of-content',None)]:
   for attempt in (1,2):
    try:
     scroll(name+'-'+str(attempt),esc)
     if rows[-1]['passed']:break
    except Exception as e:row(name+'-'+str(attempt),False,driverError=str(e),traceback=traceback.format_exc())
    finally:stop_scroll()
  try:bar()
  except Exception as e:row('2-bar-window-exclusion',False,driverError=str(e),traceback=traceback.format_exc())
 except Exception as e:row('driver-error',False,driverError=str(e),traceback=traceback.format_exc());raise
 finally:
  stop_scroll()
  if rid:
   try:call('recording.cancel',{'id':rid})
   except Exception:pass
  if fixture and fixture.poll() is None:fixture.terminate();fixture.wait(10)
  self.stop_resident(b);self.close_cover()
 return 0
r.Driver.main=flow
sys.exit(r.main())
