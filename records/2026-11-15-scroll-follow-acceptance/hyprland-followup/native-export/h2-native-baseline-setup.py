"""Run after candidate campaign ends; no compilation or distro changes."""
import os,json,subprocess,shutil,hashlib,socket,stat,errno
from pathlib import Path
P=Path.home()/'work/sfa15';B=P/'b';TREE='4346aa6ecf750b5cceb4dcedf6c10e5c11279ad3'
os.environ.update(json.loads((P/'session-env.json').read_text()))
import accept as C
for n in ['putgd-record','firefox']:
 assert not subprocess.run(['pgrep','-x',n],capture_output=True,text=True).stdout.strip(),'Finish candidate campaign before baseline setup: '+n
C.stop()
for n in ['putgd','putgd-ui','putgd-record','firefox']:
 assert not subprocess.run(['pgrep','-x',n],capture_output=True,text=True).stdout.strip(),n
assert hashlib.sha256((P/'nightly.AppImage').read_bytes()).hexdigest()=='0b60880785851dee4febd216998dc0d2d00bfada167d7cc366eb7c254b198695'
(P/'nightly.AppImage').chmod(0o700)
assert not B.exists();B.mkdir(mode=0o700)
rt=Path('/tmp/sb25');assert not rt.exists();rt.mkdir(mode=0o700);(rt/'hypr').symlink_to('/run/user/1000/hypr',target_is_directory=True)
sig=os.environ['HYPRLAND_INSTANCE_SIGNATURE'];paths=[rt/'putgd/session.sock',rt/'hypr'/sig/'.socket.sock',rt/'hypr'/sig/'.socket2.sock']
rows=[{'text':str(f),'textUtf8Bytes':len(str(f).encode()),'resolved':str(f.resolve()),'resolvedUtf8Bytes':len(str(f.resolve()).encode())}for f in paths];assert all(x['textUtf8Bytes']<=107 and x['resolvedUtf8Bytes']<=107 for x in rows)
(B/'socket-preflight.json').write_text(json.dumps(rows,indent=1))
with (B/'extract.log').open('w')as f:subprocess.run([str(P/'nightly.AppImage'),'--appimage-extract'],cwd=B,stdout=f,check=True)
for n in ['live7.py','rfb.py','umouse-native.py','ukey-native.py','ukey-ready-native.py','session-env.json']:shutil.copyfile(P/n,B/n)
(B/'session-env.json').chmod(0o600)
s=(P/'accept.py').read_text().replace('/tmp/sh25','/tmp/sb25');(B/'accept.py').write_text(s)
s=(P/'guest-agent.py').read_text().replace("P=Path.home()/'work/sfa15'","P=Path.home()/'work/sfa15/b'")
s=s.replace("os.environ['SFA_DESKTOP']=","os.environ['SFA_ROOT']=str(P)\nos.environ['SFA_EXPECT_TREE']='"+TREE+"'\nos.environ['SFA_DESKTOP']=",1);(B/'guest-agent.py').write_text(s)
(B/'tools').mkdir();(B/'tools/firefox').symlink_to(P/'tools/firefox',target_is_directory=True)
(B/'cli').write_text('#!/bin/sh\nexport LD_LIBRARY_PATH='+str(B)+'/squashfs-root/usr/lib:'+str(B)+'/squashfs-root/usr/lib/putgd\nexec '+str(B)+'/squashfs-root/usr/bin/putgd-cli --socket /tmp/sb25/putgd/session.sock "$@"\n');(B/'cli').chmod(0o700)
# Launch/import in a fresh interpreter to avoid the candidate's cached module.
script="""import os,json,time,subprocess,socket,stat,errno
from pathlib import Path
os.environ.update(json.loads(Path('session-env.json').read_text()));os.environ['SFA_ROOT']=str(Path.cwd());os.environ['SFA_EXPECT_TREE']='TREE'
import accept as A
A.start()
s=A.rpc('settings.get');d=s['document'];before=d['preferences']['scrollCaptureFromTop'];d['preferences']['scrollCaptureFromTop']=False;A.rpc('settings.save',{'document':d,'expectedRevision':s['metadata']['observedRevision']});A.rpc('settings.reload')
Path('from-top-comparison.json').write_text(json.dumps({'default':before,'tested':False,'reason':'Match candidate private configuration'}))
A.stop()
f=Path('/tmp/sb25/putgd/session.sock')
if f.exists():
 s=f.lstat();assert stat.S_ISSOCK(s.st_mode)and s.st_uid==os.getuid();assert not subprocess.run(['pgrep','-x','putgd'],capture_output=True,text=True).stdout.strip();q=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);c=q.connect_ex(str(f));q.close();assert c==errno.ECONNREFUSED;f.unlink()
""".replace("'TREE'",repr(TREE))
with (B/'start.log').open('w')as f:subprocess.run(['python3','-c',script],cwd=B,stdout=f,stderr=subprocess.STDOUT,check=True)
cold=(P/'guest-cold-start.py').read_text().replace("/'work/sfa15'","/'work/sfa15/b'").replace('bd64ffc5ac593690430bdbabb7e1f9ce6964de7e',TREE)
cold=cold.replace('import accept as A',"os.environ['SFA_ROOT']=str(P)\nos.environ['SFA_EXPECT_TREE']='"+TREE+"'\nimport accept as A")
(B/'cold-start.py').write_text(cold)
with (B/'cold-start.log').open('w')as f:subprocess.run(['python3','cold-start.py'],cwd=B,stdout=f,stderr=subprocess.STDOUT,check=True)
print(json.dumps({'baselineRoot':str(B),'tree':TREE,'runtime':str(rt),'allLocal':True}))
