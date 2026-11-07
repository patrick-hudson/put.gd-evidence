import os,sys,time,subprocess,pathlib
root=pathlib.Path.home()/'work/f9t'; pid=int(sys.argv[1]); real=sys.argv[2]=='yes'
while pathlib.Path('/proc/%d'%pid).exists(): time.sleep(2)
base=['python3',str(root/'tools/lab/record_x13.py'),'--build','candidate='+str(next((pathlib.Path.home()/'work/ff9-rec-1249/candidate').glob('*.AppImage'))),'--build','nightly='+str(next((pathlib.Path.home()/'work/ff9-rec-1249/nightly').glob('*.AppImage'))),'--analyzer',str(root/'analyzer/squashfs-root'),'--rounds','1','--frames','--video-size','800x450','--vnc-port','0']
if real:base+=['--real-data-home']
for mode,args in [('still',['--format','mp4','webm','gif','webp','--pause-at','2','--pause-for','0','--after','1']),('marker',['--format','mp4','webm','gif','webp','--pause-at','8','--pause-for','3','--after','8','--audio-device',sys.argv[3]])]:
 run=root/mode
 assert not run.exists()
 env=dict(os.environ,PUTGD_RECORD_ADAPTIVE_RATE='off',PUTGD_RECORD_DEBUG_LOG=str(root/('debug-'+mode+'.log')))
 with open(root/(mode+'.log'),'w') as log:
  subprocess.run(base+['--run',str(run),'--video',mode]+args,stdout=log,stderr=subprocess.STDOUT,env=env)
