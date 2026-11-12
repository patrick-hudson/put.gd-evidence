from pathlib import Path
import subprocess,json,os,hashlib
P=Path('/home/patrick/work/sa2');out=[]
for f in P.glob('fa*/d/putgd/file-manager/putgd-upload'):
 assert f.is_file() and not f.is_symlink() and f.stat().st_uid==os.getuid()
 r=subprocess.run(['/bin/sh',str(f),'--stop-watch'],capture_output=True,text=True,timeout=30);out.append({'launcher':str(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
(P/'watcher-cleanup.json').write_text(json.dumps(out,indent=2));print([(v['launcher'],v['returncode']) for v in out])
