from pathlib import Path
import subprocess,os
r=Path.home()/'work/f9t'
base=['python3',str(r/'hidden.py'),'record_x13','--build','candidate='+str(next((Path.home()/'work/ff9-rec-1249/candidate').glob('*.AppImage'))),'--build','nightly='+str(next((Path.home()/'work/ff9-rec-1249/nightly').glob('*.AppImage'))),'--analyzer',str(r/'analyzer/squashfs-root'),'--rounds','1','--frames','--target','region','--rect','80,40,1120,700','--video-size','800x450','--vnc-port','0']
for name,mode,timing,formats in [('region','pattern',['3','2','3'],['mp4','webm','gif','webp']),('frozen','still',['2','0','1'],['mp4','webm','gif','webp']),('av3','marker',['8','3','8'],['mp4','webm'])]:
 cmd=base+['--run',str(r/name),'--video',mode,'--pause-at',timing[0],'--pause-for',timing[1],'--after',timing[2],'--format']+formats
 if mode=='marker':cmd+=['--audio-device','@DEFAULT_SINK@']
 with open(r/(name+'.log'),'w') as log:subprocess.run(cmd,env=dict(os.environ,PUTGD_RECORD_ADAPTIVE_RATE='off'),stdout=log,stderr=log)
