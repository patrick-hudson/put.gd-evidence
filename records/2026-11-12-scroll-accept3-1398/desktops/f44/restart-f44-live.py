from pathlib import Path
import os,signal,json,time,subprocess
P=Path('/home/patrick/work/s3a');owned=[]
for d in Path('/proc').iterdir():
 if not d.name.isdigit():continue
 try:
  args=(d/'cmdline').read_bytes().split(bytes([0]))
  if len(args)>1 and args[1] in [b'live-accept3.py',str(P/'live-accept3.py').encode()] and (d/'cwd').resolve()==P:owned.append(int(d.name))
 except OSError:pass
for pid in owned:os.kill(pid,15)
time.sleep(1)
import live7 as l
os.environ['SF7']=str(P)
# Import-time P is configured by the controller's SF7 environment.
l.browser_stop();renamed=[]
for d in sorted((P/'runs').glob('accept3-*')):
 if d.is_dir() and not (d/'result.json').exists():
  to=d.with_name(d.name+'-harness-attempt1');d.rename(to);renamed.append({'from':d.name,'to':to.name})
(P/'live-harness-attempt1.json').write_text(json.dumps({'killedExactControllerPids':owned,'unqualifiedDirectories':renamed,'reason':'Firefox Marionette refused a new connection because its previous session was still active; corrected harness explicitly deletes each session and closes sockets.'},indent=2))
with (P/'live-retry.console').open('w') as log:
 r=subprocess.run(['python3',str(P/'live-accept3-v2.py'),'campaign','accept3','firefox,chromium','pr,wiki,py,mdn,repo,hn,rust','half,top'],stdout=log,stderr=subprocess.STDOUT,env=dict(os.environ,SF7=str(P),SF7_VNC='5901',SF7_NOVERIFY='1',ACCEPT3_MAX_HEIGHT='60000'))
print('LIVE_RETRY_EXIT',r.returncode,flush=True)
