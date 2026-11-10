import pathlib,subprocess,json,time,os
H=pathlib.Path.home();root=H/'n';root.mkdir(mode=0o700,exist_ok=True)
base=['python3',str(H/'click_driver.py'),'--build','pr=/usr/bin','--analyzer','/','--video','marker','--video-size','640x360','--rounds','1','--no-notifications','--keep-unpaired','--lead','6','--frames','--vnc-port','0','--click-vnc','10.0.2.2:5964','--format','mp4','--system','tone','--pause-for','0','--pause-at','14','--after','2','--click','4,200,100,left','--click','8,640,100,right','--click','12,900,100,middle','--hide-bar']
plan=[('m-still',['--target','monitor']),('m-sweep',['--target','monitor','--sweep-pointer']),('r-still',['--target','region','--rect','0,0,1280,720']),('r-sweep',['--target','region','--rect','0,0,1280,720','--sweep-pointer']),('off',['--target','monitor','--click-highlights','off','--sweep-pointer']),('h',['--target','monitor','--delayed-capture','desktop:3'])]
for name,opts in plan:
 run=root/name;run.mkdir(mode=0o700,exist_ok=True)
 cmd=base+['--run',str(run)]+opts
 env=dict(os.environ,PUTGD_RECORD_DEBUG_LOG=str(run/'helper.debug'))
 (root/(name+'.command.json')).write_text(json.dumps(dict(command=cmd,PUTGD_RECORD_DEBUG_LOG=env['PUTGD_RECORD_DEBUG_LOG'])))
 print(time.strftime('%FT%TZ',time.gmtime()),name,flush=True)
 with (root/(name+'.log')).open('w') as f:rc=subprocess.run(cmd,env=env,stdout=f,stderr=subprocess.STDOUT).returncode
 print(name,'exit',rc,flush=True)
 # Continue distinct requested cases so a failed one is retained and does not hide later coverage.
(root/'done').touch()
