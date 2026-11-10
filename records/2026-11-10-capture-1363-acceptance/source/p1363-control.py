import sys,subprocess,shlex,json
from importlib.machinery import SourceFileLoader
c=SourceFileLoader('c','/tmp/p1363-campaign.py').load_module();d=sys.argv[1];h,r,p,g,pin,port,vnc,k,known,wall=c.PROFILES[d];key='/home/patrick/work/put.gd/work/lab-bootstrap-'+k+'/identity'
subprocess.run(['rsync','-q','-e',' '.join(c.ssh(h)[:-1]),'/tmp/p1363-gui.py',c.ssh(h)[-1]+':/tmp/p1363-gui.py'],check=True)
command=shlex.join(['python3','/tmp/p1363-gui.py',r,key,d,*sys.argv[2:]])
result=subprocess.run(c.ssh(h)+[command],capture_output=True,text=True)
record=json.dumps({'mode':sys.argv[2],'arguments':sys.argv[3:],'returnCode':result.returncode,'stdout':result.stdout,'stderr':result.stderr})
writer='from pathlib import Path;p=Path.home()/"work/i1363/work/acceptance-1363"/'+repr(r)+'/"gui-command-transcript.jsonl";p.open("a").write('+repr(record+'\n')+')'
c.remote(h,shlex.join(['python3','-c',writer]));sys.stdout.write(result.stdout);sys.stderr.write(result.stderr)
if result.returncode:raise SystemExit(result.returncode)
if sys.argv[2] in ['photo','click','move','right','scroll']:
 name=sys.argv[3] if sys.argv[2]=='photo' else sys.argv[6] if sys.argv[2]=='scroll' else sys.argv[5]
 subprocess.run(['rsync','-q','-e',' '.join(c.ssh(h)[:-1]),c.ssh(h)[-1]+':/home/patrick/work/i1363/work/acceptance-1363/'+r+'/'+name+'.png','/tmp/p1363-'+r+'-'+name+'.png'],check=True)
