"""Private input/measurement wrapper; imports the pushed driver unchanged.
Sweep input and click-effect reference only; recording/capture/frame gates stay original.
"""
import importlib.util,pathlib,sys,time,math,json
HERE=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(HERE/'lab'))
spec=importlib.util.spec_from_file_location('pushed_driver',HERE/'lab/record_run-hide-bar.py');base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
swept='--sweep-pointer' in sys.argv
if swept:sys.argv.remove('--sweep-pointer')
class Driver(base.Driver):
 def cli(self,build,method,params=None,timeout=60):
  result=super().cli(build,method,params,timeout)
  if method=='recording.inspect' and result.get('state') in ('ready','recording','paused','reviewing'):
   with (self.run/'inspect.jsonl').open('a') as f:f.write(json.dumps(result)+'\n')
  return result
 def press_clicks(self,started,sent):
  if not swept:return super().press_clicks(started,sent)
  import rfb
  host,_,port=self.args.click_vnc.rpartition(':');client=rfb.RFB(int(port),host=host);events=[];plan=self.clicks();next_click=0;release=None;end=started+self.args.pause_at+self.args.after
  try:
   while time.monotonic()<end:
    now=time.monotonic();s=now-started
    if release and now>=release[0]:
     client.pointer_button(release[1],release[2],release[3],False);release=None
    if next_click<len(plan) and s>=plan[next_click][0]:
     when,x,y,button=plan[next_click];client.pointer(x,y);client.pointer_button(x,y,button,True)
     sent.append({'s':round(time.monotonic()-started,3),'movedS':round(s,3),'x':x,'y':y,'button':button})
     events.append([round(s,4),x,y,'press']);release=(now+.06,x,y,button);next_click+=1
    elif release:
     # Keep moving while held, within a couple of pixels so this stays a click, not a drag.
     x=release[1]+int(1.5*math.sin(s*80));y=release[2];client.pointer(x,y);events.append([round(s,4),x,y,'held'])
    else:
     # Away from click watch boxes and marker/flash; continuously changed coordinates at ~60 Hz.
     x=round(640+460*math.sin(s*2.4));y=round(180+25*math.sin(s*4.1));client.pointer(x,y);events.append([round(s,4),x,y,'sweep'])
    time.sleep(.016)
  except Exception as error:sent.append({'error':str(error)})
  finally:
   if release:client.pointer_button(release[1],release[2],release[3],False)
   client.close();(self.run/'pointer-events.json').write_text(json.dumps(events))
base.Driver=Driver
raise SystemExit(base.main(sys.argv[1:]))
