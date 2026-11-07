import os,sys,time,subprocess,pathlib
root=pathlib.Path.home()/'work/f9t'; pid=int(sys.argv[1]); real=sys.argv[2]=='yes'
while pathlib.Path('/proc/%d'%pid).exists(): time.sleep(2)
base=['python3',str(root/'aurora.py'),'--build','candidate='+str(next((pathlib.Path.home()/'work/ff9-rec-1249/candidate').glob('*.AppImage'))),'--build','nightly='+str(next((pathlib.Path.home()/'work/ff9-rec-1249/nightly').glob('*.AppImage'))),'--analyzer',str(root/'analyzer/squashfs-root'),'--rounds','1','--frames']
if real:base+=['--real-data-home']
for mode,args in [('pattern',['--format','mp4','webm','gif','webp','--pause-at','3','--pause-for','2','--after','3']),('marker',['--format','mp4','webm','gif','webp','--pause-at','8','--pause-for','3','--after','8','--audio-device',sys.argv[3]])]:
 run=root/mode
 assert not run.exists()
 env=dict(os.environ,PUTGD_RECORD_ADAPTIVE_RATE='off',PUTGD_RECORD_DEBUG_LOG=str(root/('debug-'+mode+'.log')))
 with open(root/(mode+'.log'),'w') as log:
  subprocess.run(base+['--run',str(run),'--video',mode]+args,stdout=log,stderr=subprocess.STDOUT,env=env)
