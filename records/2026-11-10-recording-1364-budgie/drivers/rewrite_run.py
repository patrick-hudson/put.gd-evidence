import sys,subprocess,threading,time,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'lab'))
import record_run
old=record_run.Driver.press_clicks
def presses(self,started,sent):
 env,_=record_run.session_environment()
 key=['gsettings','get','org.gnome.desktop.peripherals.mouse','natural-scroll']
 before=subprocess.check_output(key,env=env,text=True).strip()
 rc=Path.home()/'.config/budgie-desktop/labwc/rc.xml'
 report={'before':before,'xmlBefore':rc.read_text()}
 def change():
  time.sleep(max(0,started+5-time.monotonic()))
  subprocess.run(['gsettings','set','org.gnome.desktop.peripherals.mouse','natural-scroll','false' if before=='true' else 'true'],env=env,check=True)
  report['samples']=[]
  for _ in range(30):
   report['samples'].append(rc.read_text().count('putgd="click-highlights"'));time.sleep(.1)
  report['xmlDuring']=rc.read_text()
 t=threading.Thread(target=change);t.start()
 try:old(self,started,sent)
 finally:
  t.join();subprocess.run(['gsettings','set','org.gnome.desktop.peripherals.mouse','natural-scroll',before],env=env)
  (self.run/'rewrite.json').write_text(json.dumps(report,indent=2))
record_run.Driver.press_clicks=presses
record_run.main()
