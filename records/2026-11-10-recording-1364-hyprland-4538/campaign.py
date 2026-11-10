import subprocess as sp,os,json,time,pathlib
H=pathlib.Path.home();root=H/'r';root.mkdir(mode=0o700,exist_ok=True)
base=['python3',str(H/'lab/record_run.py'),'--build','pr=/usr/bin','--analyzer','/','--video','marker','--video-size','640x360','--rounds','1','--no-notifications','--keep-unpaired','--lead','6','--frames','--vnc-port','0','--click-vnc','10.0.2.2:5964']
region=['--target','region','--rect','0,0,960,540']
plan=[('a',region+['--format','mp4','webm','--mic','virtual','--system','off','--pause-for','0','--pause-at','12','--after','2']),('b',region+['--format','mp4','webm','--mic','virtual','--system','tone','--pause-for','3','--pause-at','8','--after','8'])]
for i in range(1,4):plan.append(('c'+str(i),region+['--format','webm','--mic','off','--system','tone','--pause-for','0','--pause-at','14','--after','2']))
plan += [('d',region+['--format','mp4','--mic','muted','--system','tone','--pause-for','0','--pause-at','10','--after','2']),('e',region+['--format','mp4','--mic','virtual','--system','leak','--unplug-at','6','--pause-for','0','--pause-at','12','--after','2']),('f',region+['--format','mp4','--mic','late','--system','off','--pause-for','0','--pause-at','8','--after','2'])]
click=['--format','mp4','--system','tone','--pause-for','0','--pause-at','14','--after','2','--click','4,200,100,left','--click','8,640,100,right','--click','12,900,100,middle']
for target in ('monitor','region','window'):
 plan.append(('g-'+target,(['--target',target]+(['--rect','0,0,1280,400'] if target=='region' else []))+click))
plan.append(('g-off',['--target','monitor']+click+['--click-highlights','off']))
plan.append(('h',['--target','monitor']+click+['--delayed-capture','desktop:3']))
for name,opts in plan:
 cmd=base+['--run',str(root/name)]+opts
 (root/(name+'.command.json')).write_text(json.dumps(cmd))
 print(time.strftime('%H:%M:%S'),name,flush=True)
 with (root/(name+'.log')).open('w') as f: rc=sp.run(cmd,stdout=f,stderr=sp.STDOUT).returncode
 print(name,'DONE',rc,flush=True)
night=H/'nightly.AppImage';night.chmod(0o700)
cmd=base+['--run',str(root/'nightly'),'--build','nightly='+str(night)]+region+['--format','mp4','webm','--mic','off','--system','tone','--pause-for','0','--pause-at','14','--after','2']
# Replace the PR entry, keeping one build for the independent control.
i=cmd.index('--build');cmd[i+1]='nightly='+str(night);j=cmd.index('--build',i+1);del cmd[j:j+2]
with (root/'nightly.log').open('w') as f:rc=sp.run(cmd,stdout=f,stderr=sp.STDOUT).returncode
print('nightly',rc,flush=True)
for name,env in [('g-cancel',{'LAB_CANCEL':'1'}),('g-kill',{'LAB_KILL':'1'})]:
 cmd=base+['--run',str(root/name),'--target','monitor']+click
 with (root/(name+'.log')).open('w') as f:rc=sp.run(cmd,env=dict(os.environ,**env),stdout=f,stderr=sp.STDOUT).returncode
 print(name,rc,flush=True)
(root/'done').touch()
