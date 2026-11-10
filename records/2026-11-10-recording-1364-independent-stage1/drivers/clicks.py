import sys,subprocess,pathlib,json,time,os
home=pathlib.Path.home();pr=next((home/'apps/pr').glob('*.AppImage'));root=home/'s1';an=home/'an/squashfs-root'
cmd=[sys.executable,str(home/'lab/record_run.py'),'--run',str(root/'clicks2'),'--build','pr='+str(pr),'--analyzer',str(an),'--video','marker','--rounds','5','--no-notifications','--keep-unpaired','--target','monitor','--format','mp4','--lead','6','--system','tone','--pause-for','0','--pause-at','14','--after','2','--vnc-port','0','--click-vnc','10.0.2.2:5954','--video-size','640x360','--click','4,200,100,left','--click','8,640,100,right','--click','12,1100,100,middle']
with (root/'clicks2.log').open('w') as f:rc=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT).returncode
print('clicks done',rc,flush=True)
x=json.loads((root/'clicks2/results.json').read_text()); measured=[]
for entry in x['rounds']:
    clip=root/'clicks2/out'/('pr-mp4-%d.mp4'%entry['round'])
    checks=entry['clips']['export']['clickCheck']
    rings=checks['rings']
    spans=[f"{max(0,r['firstMs']-1200)},{r['firstMs']+1500},90,720" for r in rings]
    raw=subprocess.run([str(an/'usr/bin/putgd-record'),'--click-check',str(clip),*spans],capture_output=True,text=True,check=True,env=dict(os.environ,APPDIR=str(an)))
    effects=json.loads(raw.stdout)['watches']
    for i,(ring,effect) in enumerate(zip(rings,effects),1):
        measured.append(dict(recording=entry['round'],click=i,ringMs=ring['firstMs'],effectMs=effect.get('firstMs'),ringMinusEffectMs=ring['firstMs']-effect['firstMs'] if effect.get('seen') else None,oldPointerDelayMs=ring.get('delayMs'),effect=effect))
(root/'ring-effect2.json').write_text(json.dumps(measured,indent=1)+'\n')
(root/'clicks2.done').touch()
