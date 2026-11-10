import pathlib,subprocess
r=pathlib.Path('/home/lab/b1364');app=str(next(r.glob('*.AppImage')))
base=['python3',str(r/'hidden.py'),'--build','pr='+app,'--analyzer',str(r/'an/squashfs-root'),'--video','marker','--rounds','1','--no-notifications','--keep-unpaired','--vnc-port','0','--click-vnc','10.0.2.2:5946','--video-size','640x360','--frames','--format','mp4','--mic','off','--lead','6','--system','tone','--pause-for','0','--pause-at','14','--after','2','--target','monitor','--click','4,200,100,left','--click','8,640,100,right','--click','12,1100,100,middle']
for tag,opts in [('f-monitor-retained3',[]),('f-rewrite-retained3',['--rewrite'])]:
 with open(r/(tag+'.log'),'w')as f:p=subprocess.run(base+['--run',str(r/'r'/tag)]+opts,stdout=f,stderr=subprocess.STDOUT)
 print(tag,p.returncode,flush=True)
subprocess.run(['python3',str(r/'measure_clicks.py'),'f-monitor-retained3','f-region','f-rewrite-retained3'])
