import sys,subprocess,os,time
from pathlib import Path
root=Path.home()/'work/f9t';pid=int(sys.argv[1]);engine=sys.argv[2];real=sys.argv[3]=='yes'
while pid and Path('/proc/%d'%pid).exists():time.sleep(2)
base=['python3',str(root/'hidden.py'),engine,'--build','candidate='+str(next((Path.home()/'work/ff9-rec-1249/candidate').glob('*.AppImage'))),'--build','nightly='+str(next((Path.home()/'work/ff9-rec-1249/nightly').glob('*.AppImage'))),'--analyzer',str(root/'analyzer/squashfs-root'),'--rounds','1','--frames']
if real:base+=['--real-data-home']
for name,mode,args in [('redo','pattern',['--format','mp4','webm','gif','webp','--pause-at','3','--pause-for','2','--after','3']),('av2','marker',['--format','mp4','webm','--pause-at','8','--pause-for','3','--after','8','--audio-device',sys.argv[4]])]:
 if name=='redo' and sys.argv[5]=='skip':continue
 with open(root/(name+'.log'),'w') as log:subprocess.run(base+['--run',str(root/name),'--video',mode]+args,env=dict(os.environ,PUTGD_RECORD_ADAPTIVE_RATE='off'),stdout=log,stderr=log)
