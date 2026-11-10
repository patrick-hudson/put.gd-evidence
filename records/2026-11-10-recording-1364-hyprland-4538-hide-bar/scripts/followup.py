import pathlib,subprocess,json,time
H=pathlib.Path.home();root=H/'f';root.mkdir(mode=0o700,exist_ok=True)
base=['python3',str(H/'lab/record_run-hide-bar.py'),'--build','pr=/usr/bin','--analyzer','/','--video','marker','--video-size','640x360','--rounds','1','--no-notifications','--keep-unpaired','--lead','6','--frames','--vnc-port','0','--click-vnc','10.0.2.2:5964','--target','monitor','--format','mp4','--system','tone','--pause-for','0','--pause-at','14','--after','2','--click','4,200,100,left','--click','8,640,100,right','--click','12,900,100,middle','--hide-bar']
for name,opts in [('monitor-on',[]),('monitor-off',['--click-highlights','off']),('h',['--delayed-capture','desktop:3'])]:
 cmd=base+['--run',str(root/name)]+opts
 (root/(name+'.command.json')).write_text(json.dumps(cmd))
 print(time.strftime('%FT%TZ',time.gmtime()),name,flush=True)
 with (root/(name+'.log')).open('w') as f:rc=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT).returncode
 print(name,'exit',rc,flush=True)
 if rc:break
(root/'done').touch()
