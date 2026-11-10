import sys,json,pathlib,hashlib,os,time,threading
root=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(root/'lab'));import record_run_new as record_run
class SharedBuild:
 def __init__(self,label,path,run):
  self.label=label;self.path=pathlib.Path(path).resolve();self.launcher=[str(self.path),'--background'];self.cli=str(root/'an/squashfs-root/usr/bin/putgd-cli');self.identity={'kind':'appimage','file':self.path.name,'sha256':hashlib.sha256(self.path.read_bytes()).hexdigest()}
def shared_open(self):
 assert self.args.mic=='off' and self.args.system=='tone'
 s=json.loads((root/'motion-audio.json').read_text());self.args.audio_device=s['systemSink'];return s
record_run.Build=SharedBuild;record_run.Driver.open_microphone=shared_open;record_run.Driver.close_microphone=lambda self:{'sharedSinkStillActive':True,'teardown':'motion batch finally'}
mode=os.environ.get('PUTGD_LAB_MOTION')
if mode:
 import rfb
 original_cli=record_run.Driver.cli
 def cli(self,build,method,params=None,timeout=60):
  if method=='recording.prepare':
   self.pointer=rfb.RFB(5946,host='10.0.2.2');self.pointer_lock=threading.Lock();self.pointer.pointer(200,100);time.sleep(.4);self.sweep_stop=threading.Event();self.sweep_count=0;self.sweep_pos=[200,100];self.sweep_started=None
  if method=='recording.start' and mode=='sweep':
   def sweep():
    began=time.monotonic();self.sweep_started=began
    while not self.sweep_stop.is_set():
     # Smooth triangular horizontal sweep, 720 px/s, 60 input updates/s.
     q=((time.monotonic()-began)*720+100)%2160
     x=round(100+(q if q<=1080 else 2160-q))
     with self.pointer_lock:self.pointer.pointer(x,100);self.sweep_pos=[x,100];self.sweep_count+=1
     self.sweep_stop.wait(1/60)
   self.sweep_thread=threading.Thread(target=sweep,daemon=True);self.sweep_thread.start()
  try:return original_cli(self,build,method,params,timeout)
  finally:
   if method=='recording.stop':
    self.sweep_stop.set()
    if hasattr(self,'sweep_thread'):self.sweep_thread.join(5)
    self.pointer.close();(self.run/'pointer-motion.json').write_text(json.dumps({'mode':mode,'updates':self.sweep_count,'startedMonotonic':self.sweep_started,'stoppedMonotonic':time.monotonic(),'initial':[200,100],'y':100,'rangeX':[100,1180],'speedPxS':720,'requestedHz':60}))
 def presses(self,started,sent):
  for seconds,_,_,button in self.clicks():
   time.sleep(max(0,started+seconds-time.monotonic()))
   with self.pointer_lock:
    x,y=self.sweep_pos;self.pointer.pointer_button(x,y,button,True);sent.append({'s':time.monotonic()-started,'x':x,'y':y,'button':button,'mode':mode})
   time.sleep(.06)
   with self.pointer_lock:self.pointer.pointer_button(*self.sweep_pos,button,False)
 def no_click_measure(self,*args,**kwargs):return {'scope':'audio-only cursor-motion experiment','mode':mode,'ringsNotMeasured':True}
 record_run.Driver.cli=cli;record_run.Driver.press_clicks=presses;record_run.Driver.click_check=no_click_measure
# Observe bindings immediately after production Stop, before cancel/quit.
stop_cli=record_run.Driver.cli
def track_stop(self,build,method,params=None,timeout=60):
 r=stop_cli(self,build,method,params,timeout)
 if method=='recording.stop':
  rc=pathlib.Path.home()/'.config/budgie-desktop/labwc/rc.xml';b=rc.read_bytes();(self.run/'rc-after-stop.xml').write_bytes(b);(self.run/'after-stop.json').write_text(json.dumps({'clickMarkers':b.decode().count('putgd="click-highlights"'),'sha256':hashlib.sha256(b).hexdigest(),'state':r.get('state')}))
 return r
record_run.Driver.cli=track_stop
sys.exit(record_run.main())
