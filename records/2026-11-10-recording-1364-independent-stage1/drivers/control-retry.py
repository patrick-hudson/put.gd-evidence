import sys, subprocess, pathlib, json, time, os
home=pathlib.Path.home(); root=home/'s1'; root.mkdir(mode=0o700,exist_ok=True)
pr=next((home/'apps/pr').glob('*.AppImage')); nightly=next((home/'apps/nightly').glob('*.AppImage'))
for app in (pr,nightly):app.chmod(0o700)
an=home/'an';an.mkdir(exist_ok=True)
subprocess.run([str(pr),'--appimage-extract'],cwd=an,stdout=subprocess.DEVNULL,check=True)
an=an/'squashfs-root'
base=[sys.executable,str(home/'lab/record_run.py'),'--analyzer',str(an),'--video','marker','--rounds','1','--no-notifications','--keep-unpaired','--target','region','--rect','0,0,960,540','--format','mp4','webm','--lead','6','--pause-for','0','--pause-at','14','--after','2','--vnc-port','0','--video-size','640x360','--min-pairs','10','--frames']
plan=[]
for i in range(1,4):
    for label,app in ([('nightly',nightly),('pr',pr)] if i%2 else [('pr',pr),('nightly',nightly)]):plan.append((f'sys-{i}-{label}',label,app,['--mic','off','--system','tone']))
    for mode,system in [('mic','off'),('mixed','tone')]:plan.append((f'{mode}-{i}-pr','pr',pr,['--mic','virtual','--system',system]))
if sys.argv[1]=='hypr':plan=[p for p in plan if '-1-' in p[0]]
plan=[p for p in plan if not p[0].startswith('mixed-')]
for name,label,app,opts in plan:
    cmd=base+['--run',str(root/name),'--build',label+'='+str(app)]+opts
    print(time.strftime('%H:%M:%S'),name,flush=True)
    with (root/(name+'.log')).open('w') as out:rc=subprocess.run(cmd,stdout=out,stderr=subprocess.STDOUT).returncode
    print('DONE',name,rc,flush=True)
    if rc:print((root/(name+'.log')).read_text()[-2000:],flush=True)
(root/'retry.done').touch()
