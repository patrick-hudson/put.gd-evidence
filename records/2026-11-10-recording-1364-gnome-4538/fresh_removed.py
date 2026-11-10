# Destructive fixtures need a new driver invocation for each output format.
import json,subprocess,sys,os,time
from pathlib import Path
base=Path.home()/'work/s1364s2';lab=base/'lab';sys.path.insert(0,str(lab));import record_run
assert (base/'campaign.done').exists(), 'primary campaign still active'
env,_=record_run.session_environment()
def vm(*args):
 r=subprocess.run([sys.executable,str(lab/'virtual_mic.py'),*args],env=env,capture_output=True,text=True,check=True);return json.loads(r.stdout)
state=base/'fresh-outer.json';vm('create','--name','putgd_lab_s2_gnome2','--state',str(state),'--system-sink','--no-microphone','--monitor-default')
cases=[('lost-webm',['--mic','virtual','--system','leak','--unplug-at','6']),('output-webm',['--mic','off','--system','tone','--output-gone-at','6','--output-fallback']),('output-mic-off-webm',['--mic','muted','--mic-default','--system','tone','--output-gone-at','6','--output-fallback'])]
report=[]
try:
 for name,args in cases:
  cmd=[sys.executable,str(lab/'record_run.py'),'--run',str(base/'runs'/name),'--build','pr=/usr/bin','--analyzer','/','--video','marker','--marker-motion','--rounds','1','--no-notifications','--keep-unpaired','--min-pairs','5','--frames','--vnc-port','5901','--target','region','--rect','0,0,960,540','--format','webm','--lead','6','--pause-at','12','--pause-for','0','--after','2',*args]
  print('START',name,time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),flush=True)
  with (base/'runs'/(name+'.log')).open('w') as f:r=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT)
  report.append({'case':name,'rc':r.returncode,'command':cmd});(base/'fresh-removed.json').write_text(json.dumps(report,indent=1)+'\n')
  print('END',name,r.returncode,flush=True)
 # Correct monitor/window commands contain no region rectangle. Use the supplied case13 wrapper unchanged.
 extra=[('click-monitor-corrected',['env','LAB='+str(lab),'RUNS='+str(base/'runs'),'bash',str(base/'both_run.sh'),'click-monitor-corrected','/usr/bin','/','300,700,1100','100','--mic','off','--marker-motion','--vnc-port','5901','--min-pairs','10']),
 ('click-window-corrected',[sys.executable,str(lab/'record_run.py'),'--run',str(base/'runs/click-window-corrected'),'--build','pr=/usr/bin','--analyzer','/','--video','marker','--marker-motion','--rounds','1','--no-notifications','--keep-unpaired','--frames','--vnc-port','5901','--target','window','--format','mp4','--lead','3','--mic','off','--system','tone','--pause-at','14','--pause-for','0','--after','2','--click','4,300,100,left','--click','8,700,100,right','--click','12,1100,100,middle']),
 ('click-off-corrected',[sys.executable,str(lab/'record_run.py'),'--run',str(base/'runs/click-off-corrected'),'--build','pr=/usr/bin','--analyzer','/','--video','marker','--marker-motion','--rounds','1','--no-notifications','--keep-unpaired','--frames','--vnc-port','5901','--target','monitor','--format','mp4','--lead','3','--mic','off','--system','tone','--pause-at','14','--pause-for','0','--after','2','--click','4,300,100,left','--click','8,700,100,right','--click','12,1100,100,middle','--click-highlights','off'])]
 for name,cmd in extra:
  print('START',name,time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),flush=True)
  with (base/'runs'/(name+'.log')).open('w') as f:r=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT)
  report.append({'case':name,'rc':r.returncode,'command':cmd});(base/'fresh-removed.json').write_text(json.dumps(report,indent=1)+'\n')
  print('END',name,r.returncode,flush=True)
finally:
 (base/'fresh-outer-cleanup.json').write_text(json.dumps(vm('remove','--state',str(state)),indent=1)+'\n')
 (base/'fresh-removed.done').write_text('done\n')
