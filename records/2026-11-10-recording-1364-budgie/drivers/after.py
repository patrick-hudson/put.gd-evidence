import subprocess,pathlib,os,json
root=pathlib.Path('/home/lab/b1364');app=str(next(root.glob('*.AppImage')));an=str(root/'an/squashfs-root');runs=root/'r'
base=['--build','pr='+app,'--analyzer',an,'--video','marker','--rounds','1','--no-notifications','--keep-unpaired','--vnc-port','0','--click-vnc','10.0.2.2:5946','--video-size','640x360','--frames','--format','mp4','--mic','off','--lead','3','--system','tone','--pause-for','0','--pause-at','14','--after','2','--click','4,200,100,left','--click','8,640,100,right','--click','12,1100,100,middle']
def cmd(tag,driver,opts):
 subprocess.run(['python3',str(root/'check_socket_paths.py'),'--socket','/run/user/1000/putgd/session.sock'],check=True)
 with open(runs/(tag+'.log'),'w')as f:
  argv=['python3',str(root/driver),'--run',str(runs/tag)]+base+opts;f.write(repr(argv)+'\n');f.flush();r=subprocess.run(argv,stdout=f,stderr=subprocess.STDOUT)
 print(tag,r.returncode,flush=True)
cmd('f-rewrite','rewrite_run.py',['--target','monitor'])
cmd('f-remembered','remembered.py',['--target','window','--click-highlights','off'])
with open(root/'extra.log','w')as f:
 r=subprocess.run(['python3',str(root/'extra.py'),app,str(runs/'extra')],stdout=f,stderr=subprocess.STDOUT)
print('extra',r.returncode,flush=True)
with open(root/'click-measure.log','w')as f:
 subprocess.run(['python3',str(root/'measure_clicks.py'),'f-monitor','f-region','f-rewrite','g'],stdout=f,stderr=subprocess.STDOUT)
nightly=next((root/'nightly').glob('*.AppImage'))
args=['python3',str(root/'lab/record_run.py'),'--run',str(runs/'nightly'),'--build','nightly='+str(nightly),'--analyzer',an,'--video','marker','--rounds','1','--no-notifications','--keep-unpaired','--vnc-port','0','--video-size','640x360','--frames','--target','region','--rect','0,0,960,540','--format','mp4','webm','--lead','6','--system','tone','--pause-for','0','--pause-at','12','--after','2']
with open(root/'nightly.log','w')as f:r=subprocess.run(args,stdout=f,stderr=subprocess.STDOUT)
print('nightly',r.returncode,flush=True)
