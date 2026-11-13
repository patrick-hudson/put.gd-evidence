#!/usr/bin/env python3
import json,os,pathlib,subprocess,sys,time
import record_acceptance as setup
r=setup.r

def flow(self):
 b=r.Build(*self.args.build[0].split('=',1),self.run); term=None; rows=[]
 def row(name,**v): rows.append({'row':name,**v}); (self.run/'picker.json').write_text(json.dumps(rows,indent=2))
 def xd(*a): return subprocess.run(['xdotool',*map(str,a)],env=self.env,text=True,capture_output=True,check=True).stdout.strip()
 def hotkey(): xd('key','--delay','0','ctrl+shift+F9')
 def drag(early=False):
  xd('mousemove',400,250)
  hotkey(); time.sleep(.015 if early else .7)
  xd('mousedown',1); xd('mousemove','--sync',1050,720); xd('mouseup',1)
 def recent(): return self.cli(b,'operation.recent')['operations']
 def wait_new(old):
  for _ in range(200):
   ops=[v for v in recent() if v['id'] not in old]
   if ops and ops[0]['state'] in ('completed','failed','partial','cancelled'): return ops[0]
   time.sleep(.05)
  raise RuntimeError('hotkey did not complete')
 def input_check(name):
  # Opening the menu exposes the real panel; clicking its start button closes it.
  xd('key','Super_L'); time.sleep(.2); self.desktop_frame(self.run/'frames'/(name+'-panel-before.png'))
  xd('mousemove',20,1060); xd('click',1); time.sleep(.2); self.desktop_frame(self.run/'frames'/(name+'-panel-after.png'))
  wid=xd('search','--pid',term.pid).splitlines()[-1]; xd('windowactivate','--sync',wid)
  token='sweep-'+name
  xd('type','--clearmodifiers','--delay','0',token); xd('key','Return')
  for _ in range(50):
   if token in (self.run/'terminal-input').read_text(): break
   time.sleep(.02)
  assert token in (self.run/'terminal-input').read_text(),'terminal did not receive input'
  tree=subprocess.run(['xwininfo','-root','-tree'],env=self.env,capture_output=True,text=True,check=True).stdout
  names=[v for v in tree.splitlines() if 'putgd' in v.lower()]
  self.desktop_frame(self.run/'frames'/(name+'-terminal.png'))
  return names
 try:
  self.start_resident(b); time.sleep(3); self.stop_resident(b); self.open_cover(); self.start_resident(b)
  doc=self.cli(b,'settings.get'); self.cli(b,'settings.patch',{'patch':{'actions':{'region':{'shortcut':'Ctrl+Shift+F9'}},'preferences':{'regionSelectionMode':'live'}},'expectedRevision':doc['metadata']['observedRevision']})
  sh=self.run/'terminal.sh'; sh.write_text('while IFS= read -r v; do printf "%s\\n" "$v" >> '+str(self.run/'terminal-input')+'; done\n'); (self.run/'terminal-input').touch()
  term=subprocess.Popen(['xterm','-title','Sweep synthetic terminal','-e','sh',str(sh)],env=self.env,stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  time.sleep(.5)
  cases=['tray-drag','drag','early-drag','keyboard-enter','escape','right-click','zero-size','early-escape']
  for name in cases:
   for attempt in (1,2):
    try:
     xd('windowactivate','--sync',self.cover_x11_window()); old={v['id'] for v in recent()}
     if name=='tray-drag':
      import native_tray
      tray=native_tray.activate(self.resident.pid,'Capture region'); time.sleep(.7); xd('mousemove',400,250); xd('mousedown',1); xd('mousemove','--sync',1050,720); xd('mouseup',1)
     elif name in ('drag','early-drag'): drag(name=='early-drag')
     else:
      hotkey(); time.sleep(.015 if name=='early-escape' else .7)
      if name=='keyboard-enter': xd('key','Right','Right','Down','Return')
      elif name in ('escape','early-escape'): xd('key','Escape')
      elif name=='right-click': xd('click',3)
      else: xd('mousemove',500,500); xd('click',1)
     op=wait_new(old); names=input_check(name+'-'+str(attempt))
     expected='completed' if name in ('tray-drag','drag','early-drag','keyboard-enter') else 'cancelled'
     row(name,passed=op['state']==expected,attempt=attempt,operation=op,remainingWindows=names,visualInspectionPending=True)
     if op['state']==expected: break
    except Exception as e:
     row(name,passed=False,attempt=attempt,error=str(e)); xd('key','Escape')
  xd('windowactivate','--sync',self.cover_x11_window())
  for i in range(20): hotkey(); xd('key','--delay','0','Escape'); time.sleep(.1)
  time.sleep(1); names=input_check('twenty-cycles'); row('twenty-cycles',passed=True,remainingWindows=names,visualInspectionPending=True)
 except Exception as e: row('driver-error',passed=False,error=str(e))
 finally:
  if term: term.terminate(); term.wait(10)
  self.stop_resident(b); self.close_cover()
 return 0
r.Driver.main=flow
sys.exit(r.main())
