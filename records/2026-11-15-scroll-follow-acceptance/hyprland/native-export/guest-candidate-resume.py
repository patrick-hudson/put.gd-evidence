import os,json,subprocess,socket,stat,errno
from pathlib import Path
P=Path.home()/'work/sfa15';os.environ.update(json.loads((P/'session-env.json').read_text()));os.environ['XDG_RUNTIME_DIR']='/run/user/1000'
subprocess.run(['systemctl','--user','stop','sfa15-res.scope'],check=True)
for n in ['putgd','putgd-ui','putgd-record','firefox']:
 assert not subprocess.run(['pgrep','-x',n],capture_output=True,text=True).stdout.strip(),n
f=Path('/tmp/sh15/putgd/session.sock')
if f.exists():
 s=f.lstat();assert stat.S_ISSOCK(s.st_mode)and s.st_uid==os.getuid();q=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);code=q.connect_ex(str(f));q.close();assert code==errno.ECONNREFUSED;f.unlink()
os.environ['SFA_ROOT']=str(P);os.environ['SFA_EXPECT_TREE']='bd64ffc5ac593690430bdbabb7e1f9ce6964de7e'
subprocess.run(['python3','guest-cold-start.py'],cwd=P,check=True)
