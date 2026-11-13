from pathlib import Path
import os,time,json,sys,subprocess
from Xlib import X,XK,display,error
from Xlib.ext import xtest
from PIL import Image,ImageDraw
assert subprocess.run(['systemd-detect-virt'],capture_output=True,text=True).stdout.strip()=='none','physical host required'
cfg=json.loads(sys.argv[4]);
pid=int(sys.argv[1]);helper=Path(sys.argv[2]).resolve();out=Path(sys.argv[3]);out.mkdir(mode=0o700);d=display.Display();root=d.screen().root;assert d.screen().width_in_pixels==1920 and d.screen().height_in_pixels==1080
stamp=lambda p:Path('/proc',str(p),'stat').read_text().rsplit(') ',1)[1].split()
residentStart=stamp(pid)[19];hstat=helper.stat();atom=d.intern_atom('_NET_WM_PID');root.change_attributes(event_mask=X.SubstructureNotifyMask);d.sync();canvas=out/'canvas.png';im=Image.new('RGB',(1920,1080),(80,90,100));ImageDraw.Draw(im).text((40,45),'Synthetic capture benchmark - all selections cancelled',fill='white');im.save(canvas);canvasWindow=root.create_window(0,0,1920,1080,0,d.screen().root_depth,X.InputOutput,X.CopyFromParent,background_pixel=(80<<16)|(90<<8)|100,override_redirect=1);canvasWindow.map();canvasWindow.configure(stack_mode=X.Above);d.sync()
keys={s:d.keysym_to_keycode(XK.string_to_keysym(s)) for s in ['Control_L','Shift_L','F12','Escape']};rows=[]
def reading(p):
 fields=stamp(p);roll=Path('/proc',str(p),'smaps_rollup').read_text();kb={}
 for line in roll.splitlines():
  if line.split(':',1)[0] in ['Rss','Pss','Shared_Clean','Private_Clean']:kb[line.split(':')[0]]=int(line.split()[1])
 return {'minflt':int(fields[7]),'majflt':int(fields[9]),**kb}
def key(s,t):xtest.fake_input(d,t,keys[s])
def esc():key('Escape',X.KeyPress);key('Escape',X.KeyRelease);xtest.fake_input(d,X.ButtonRelease,1);d.sync()
def pixel(w,x,y):
 try:return list(w.get_image(x,y,1,1,X.ZPixmap,0xffffffff).data[:3])
 except error.XError:return None
def owner(w):
 try:
  a=w.get_attributes();g=w.get_geometry();p=w.get_full_property(atom,X.AnyPropertyType);who=int(p.value[0]) if p else 0
  if not a.override_redirect or (g.width,g.height)!=(1920,1080):return None
  s=stamp(who)
  if who==pid and s[19]==residentStart:return {'pid':who,'startTicks':s[19]}
  st=Path('/proc',str(who),'exe').stat()
  if int(s[1])==pid and (st.st_dev,st.st_ino)==(hstat.st_dev,hstat.st_ino):return {'pid':who,'startTicks':s[19]}
 except (error.XError,OSError,ValueError):pass
try:
 time.sleep(.2);assert pixel(root,102,151)==[100,90,80], 'own override-redirect covering canvas not visible'
 for n in range(cfg['warmups']+cfg['samples']):
  beforeQuiet=None
  if n>=cfg['warmups'] and cfg.get('quietSeconds'):
   beforeQuiet=reading(pid);qstart=time.monotonic();time.sleep(cfg['quietSeconds']);quietElapsed=time.monotonic()-qstart
  elif n>0:time.sleep(cfg.get('spacingSeconds',.2))
  before=reading(pid)
  while d.pending_events():d.next_event()
  start=time.monotonic_ns()
  for k in ['Control_L','Shift_L','F12']:key(k,X.KeyPress)
  for k in ['F12','Shift_L','Control_L']:key(k,X.KeyRelease)
  d.sync();deadline=time.monotonic()+5;window=None;identity=None
  while time.monotonic()<deadline:
   while d.pending_events():
    e=d.next_event()
    if e.type==X.MapNotify:
     found=owner(e.window)
     if found:window=e.window;identity=found
   if window:break
   time.sleep(.001)
  assert window is not None,'no exact-owned full-monitor selector MapNotify'
  mapped=time.monotonic_ns();xtest.fake_input(d,X.MotionNotify,x=100,y=150);xtest.fake_input(d,X.ButtonPress,1);xtest.fake_input(d,X.MotionNotify,x=500,y=550);d.sync();drawn=None;shown=None;deadline=time.monotonic()+5
  while time.monotonic()<deadline:
   assert owner(window)==identity,'selector ownership changed'
   if drawn is None and pixel(window,102,151)==[255]*3:drawn=time.monotonic_ns()
   if drawn and pixel(root,102,151)==[255]*3:shown=time.monotonic_ns();break
   time.sleep(.004)
  assert drawn and shown,'inner white ring not observed'
  after=reading(pid)
  row={'beforePress':before,'afterPress':after,'faultDelta':{k:after[k]-before[k] for k in ['minflt','majflt']},'beforeQuiet':beforeQuiet,'quietElapsedSeconds':quietElapsed if beforeQuiet else None,'mapMs':(mapped-start)/1e6,'drawableMs':(drawn-start)/1e6,'onScreenMs':(shown-start)/1e6,'owner':identity,'outerDrawablePixel':pixel(window,102,150),'innerDrawablePixel':pixel(window,102,151)}
  esc();time.sleep(.2)
  if n>=cfg['warmups']:rows.append(row)
  (out/'receipt.json').write_text(json.dumps({'candidateOrBaselineResidentPid':pid,'residentStartTicks':residentStart,'method':'#1085 inner-ring point102,151, XTest CtrlShiftF12, exact-owned override-redirect full-monitor selector;4msroot readback. Separate lab witness, frozen harness unmodified.','warmups':cfg['warmups'],'requestedSamples':cfg['samples'],'configuration':cfg,'rows':rows,'complete':len(rows)==cfg['samples']},indent=2))
 print('OUTLINE',len(rows),max(x['onScreenMs'] for x in rows),flush=True)
finally:
 esc()
 for k in ['F12','Shift_L','Control_L']:key(k,X.KeyRelease)
 d.sync();canvasWindow.destroy();d.sync()
