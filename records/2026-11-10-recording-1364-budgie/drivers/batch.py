import subprocess,os,json,time
from pathlib import Path
root=Path('/home/lab/b1364'); app=str(next(root.glob('*.AppImage')))
runs=root/'r';runs.mkdir(exist_ok=True)
def run(tag,opts):
 d=runs/tag
 command=['python3',str(root/'lab/record_run.py'),'--run',str(d),'--build','pr='+app,'--analyzer',str(root/'an/squashfs-root'),'--video','marker','--rounds','1','--no-notifications','--keep-unpaired','--vnc-port','0','--click-vnc','10.0.2.2:5946','--video-size','640x360','--frames']+opts
 subprocess.run(['python3',str(root/'check_socket_paths.py'),'--socket','/run/user/1000/putgd/session.sock'],check=True)
 with open(runs/(tag+'.log'),'w') as f:
  f.write('COMMAND '+repr(command)+'\n');f.flush()
  ret=subprocess.run(command,stdout=f,stderr=subprocess.STDOUT,env=dict(os.environ,PUTGD_RECORD_DEBUG_LOG=str(runs/(tag+'.debug')))).returncode
 print(tag,ret,flush=True)
 if (d/'results.json').exists():subprocess.run(['python3',str(root/'lab/summarize_run.py'),str(d/'results.json')])
 (runs/(tag+'.done')).write_text(str(ret))
region=['--target','region','--rect','0,0,960,540','--lead','6']
run('a',region+['--format','mp4','webm','--mic','virtual','--system','off','--pause-for','0','--pause-at','12','--after','2'])
run('b',region+['--format','mp4','webm','--mic','virtual','--system','tone','--pause-for','3','--pause-at','8','--after','8'])
run('c',region+['--format','mp4','--mic','muted','--system','tone','--pause-for','0','--pause-at','10','--after','2'])
run('d',region+['--format','mp4','--mic','virtual','--system','leak','--unplug-at','6','--pause-for','0','--pause-at','12','--after','2'])
run('e',region+['--format','mp4','--mic','late','--system','off','--pause-for','0','--pause-at','8','--after','2'])
click=['--format','mp4','--mic','off','--lead','3','--system','tone','--pause-for','0','--pause-at','14','--after','2','--click','4,200,100,left','--click','8,640,100,right','--click','12,1100,100,middle']
run('f-monitor',['--target','monitor']+click)
run('f-region',['--target','region','--rect','0,0,1280,400']+click)
run('f-off',['--target','region','--rect','0,0,1280,400','--click-highlights','off']+click)
rc=Path.home()/'.config/budgie-desktop/labwc/rc.xml'
(runs/'g-before.xml').write_bytes(rc.read_bytes())
run('g',['--target','monitor','--delayed-capture','desktop:3']+click)
(runs/'g-after.xml').write_bytes(rc.read_bytes())
