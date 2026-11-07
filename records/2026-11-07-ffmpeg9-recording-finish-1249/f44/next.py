import subprocess,os
from pathlib import Path
r=Path.home()/'work/r9b';base=['python3',str(r/'runner.py'),'--build','candidate='+str(next((Path.home()/'work/ff9-rec-1249b/candidate').glob('*.AppImage'))),'--build','nightly='+str(next((Path.home()/'work/ff9-rec-1249/nightly').glob('*.AppImage'))),'--analyzer',str(r/'extract/appdir-candidate/squashfs-root'),'--video-size','704x396','--target','region','--rect','80,140,1120,600','--rounds','1','--frames','--vnc-port','5901']
for name,mode,timing,formats in [('still','still',['3','0','3'],['mp4','webm','gif','webp']),('marker','marker',['8','3','8'],['mp4','webm'])]:
 cmd=base+['--run',str(r/name),'--video',mode,'--pause-at',timing[0],'--pause-for',timing[1],'--after',timing[2],'--format']+formats
 with open(r/(name+'.log'),'w') as log:subprocess.run(cmd,env=dict(os.environ,PUTGD_RECORD_ADAPTIVE_RATE='off'),stdout=log,stderr=log)
with open(r/'history.log','w') as log:subprocess.run(['python3',str(r/'history.py'),'no','unused','history'],stdout=log,stderr=log)
