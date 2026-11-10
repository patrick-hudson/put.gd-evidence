import json, subprocess, sys, time, os
from pathlib import Path
base=Path.home()/'work/s1364s2'; lab=base/'lab'; sys.path.insert(0,str(lab)); import record_run
base.joinpath('runs').mkdir(exist_ok=True)
env,_=record_run.session_environment()
paths=[env['XDG_RUNTIME_DIR']+'/putgd/session.sock',env.get('WAYLAND_DISPLAY',''),env['XDG_RUNTIME_DIR']+'/pulse/native',env['XDG_RUNTIME_DIR']+'/pipewire-0',env['XDG_RUNTIME_DIR']+'/bus']
assert all(len(p.encode())<=107 for p in paths)
(base/'socket-lengths.json').write_text(json.dumps({p:len(p.encode()) for p in paths},indent=2))
def vm(*args):
 r=subprocess.run([sys.executable,str(lab/'virtual_mic.py'),*args],env=env,capture_output=True,text=True,check=True); return json.loads(r.stdout)
outer=base/'outer.json'; vm('create','--name','putgd_lab_s2_gnome','--state',str(outer),'--system-sink','--no-microphone','--monitor-default')
cases=[
 ('system-compare',['--mic','off','--system','tone','--rounds','3','--build','nightly='+str(Path.home()/'work/s1364b/roots/nightly/usr/bin'),'--pause-at','14','--pause-for','0','--after','2']),
 ('mic',['--mic','virtual','--system','off']),
 ('mixed',['--mic','virtual','--system','tone']),
 ('off',['--mic','muted','--system','tone']),
 ('lost',['--mic','virtual','--system','leak','--unplug-at','6','--pause-at','12','--pause-for','0','--after','2']),
 ('ready',['--mic','late','--system','off','--format','mp4','--lead','3','--pause-at','8','--pause-for','0','--after','2']),
 ('output',['--mic','off','--system','tone','--output-gone-at','6','--output-fallback','--pause-at','12','--pause-for','0','--after','2']),
 ('output-mic-off',['--mic','muted','--mic-default','--system','tone','--output-gone-at','6','--output-fallback','--pause-at','12','--pause-for','0','--after','2']),
 ('refusal',['--mic','default','--system','off','--format','mp4']),
]
clicks=['--mic','off','--system','tone','--lead','3','--pause-at','14','--pause-for','0','--after','2','--format','mp4','--click','4,300,100,left','--click','8,700,100,right','--click','12,1100,100,middle']
cases += [('click-monitor',clicks+['--target','monitor','--delayed-capture','desktop:3']),('click-region',clicks+['--target','region','--rect','0,0,1280,400']),('click-window',clicks+['--target','window']),('click-off',clicks+['--target','monitor','--click-highlights','off'])]
report=[]
try:
 for name,args in cases:
  if len(sys.argv)>1 and name not in sys.argv[1:]:continue
  cmd=[sys.executable,str(lab/'record_run.py'),'--run',str(base/'runs'/name),'--build','pr=/usr/bin','--analyzer','/','--video','marker','--marker-motion','--rounds','1','--no-notifications','--keep-unpaired','--min-pairs','10','--frames','--vnc-port','5901','--target','region','--rect','0,0,960,540','--format','mp4','webm','--lead','6','--pause-at','8','--pause-for','3','--after','8',*args]
  print('START',name,time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),flush=True)
  with (base/'runs'/(name+'.log')).open('w') as log:r=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT)
  report.append({'case':name,'rc':r.returncode,'command':cmd}); (base/'campaign.json').write_text(json.dumps(report,indent=1)+'\n')
  print('END',name,r.returncode,flush=True)
finally:
 (base/'outer-cleanup.json').write_text(json.dumps(vm('remove','--state',str(outer)),indent=2))
 (base/'campaign.done').write_text('done\n')
