from pathlib import Path
import subprocess,time,os
r=Path.home()/'work/f9t'
while Path('/proc/796112').exists():time.sleep(2)
base=['python3',str(r/'hidden.py'),'record_run','--run',str(r/'pair'),'--build','nightly='+str(next((Path.home()/'work/ff9-rec-1249/nightly').glob('*.AppImage'))),'--build','candidate='+str(next((Path.home()/'work/ff9-rec-1249/candidate').glob('*.AppImage'))),'--analyzer',str(r/'analyzer/squashfs-root'),'--rounds','1','--frames','--video','pattern','--format','mp4','webm','--pause-at','3','--pause-for','2','--after','3','--real-data-home']
with open(r/'pair.log','w') as log:subprocess.run(base,env=dict(os.environ,PUTGD_RECORD_ADAPTIVE_RATE='off'),stdout=log,stderr=log)
for args in [['score.py','pair','redo','frozen3'],['collect.py']]:
 with open(r/(args[0]+'.finish.log'),'w') as log:subprocess.run(['python3',str(r/args[0])]+args[1:],stdout=log,stderr=log)
