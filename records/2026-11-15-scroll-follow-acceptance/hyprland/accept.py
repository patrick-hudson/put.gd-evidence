"""Acceptance transport: native guest product/input/browser; host analysis only."""
import os,sys,json,time,subprocess,shlex,hashlib
from pathlib import Path
P=Path.home()/'work/sfa15/guest-h';GP='/home/lab/work/sfa15';RUN=Path.home()/'work/sfa15/repo/work/lab-runs/sfa15h';state=json.loads((RUN/'state.json').read_text())
SSH=['ssh','-i',str(RUN/'identity'),'-o','IdentitiesOnly=yes','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile='+state['known_hosts'],'-p',str(state['ssh_port']),'lab@127.0.0.1']
SCP=['scp','-i',str(RUN/'identity'),'-o','IdentitiesOnly=yes','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile='+state['known_hosts'],'-P',str(state['ssh_port'])]
def remote(mode,*args):
 r=subprocess.run([*SSH,shlex.join(['python3',GP+'/guest-agent.py',mode,*args])],capture_output=True,text=True,timeout=110)
 if r.returncode:raise RuntimeError('Guest '+mode+' failed: '+r.stderr)
 value=json.loads(r.stdout)
 if mode=='anchor':
  with (P/'anchor-events.jsonl').open('a')as f:f.write(json.dumps(value)+'\n')
 return value
def sync_artifact(sid):
 dst=P/'archive/images'/(sid+'.png');dst.parent.mkdir(parents=True,exist_ok=True)
 if dst.exists():return dst
 r=remote('artifact',sid);subprocess.run([*SCP,'lab@127.0.0.1:'+r['local']['path'],str(dst)],check=True,capture_output=True)
 assert hashlib.sha256(dst.read_bytes()).hexdigest()==r['sha256'];(P/'transport-artifacts').mkdir(exist_ok=True);(P/'transport-artifacts'/(sid+'.json')).write_text(json.dumps(r,indent=1));return dst
def rpc(m,p={}):
 r=subprocess.run([str(P/'cli'),m,json.dumps(p)],capture_output=True,text=True,timeout=110);o=json.loads(r.stdout)
 if not o.get('ok'):raise RuntimeError(o)
 v=o['result']
 if m=='history.list':
  # Keep the raw guest result separately; local paths below identify verified
  # transported copies so supplied analysis scripts can read the real PNG.
  with (P/'transport-history.jsonl').open('a')as f:f.write(json.dumps(v)+'\n')
  for row in v.get('records',[]):
   if row.get('local',{}).get('path')and row.get('operationId'):
    original=row['local']['path'];row['local']['path']=str(sync_artifact(row['operationId']));row['transportOriginalPath']=original
 return v
DESKTOP='Hyprland0.56.2 Omarchy4.5.0 KVM guest'
E=dict(os.environ,XDG_SESSION_TYPE='wayland',XDG_CURRENT_DESKTOP='Hyprland',SF7_VNC='5940',SFA_NATIVE_POINTER='1',SFA_MCP_ROOT=str(P),SFA_MCP_SOCKET='/tmp/sh15/putgd/session.sock',SFA_MCP_PYTHON=str(Path.home()/'work/i1363/tools/mcp/.venv/bin/python'))
for k in ['DISPLAY','WAYLAND_DISPLAY','XAUTHORITY']:E.pop(k,None)
os.environ.update({k:E[k]for k in ['SF7_VNC','SFA_NATIVE_POINTER','SFA_MCP_ROOT','SFA_MCP_SOCKET','SFA_MCP_PYTHON']})
sys.path.insert(0,str(P));import live7 as L
L.P=P;L.session_env=lambda:(E,DESKTOP)
def browser_start(kind):
 assert not remote('helper-pids'),'A guest helper is still running'
 d=remote('browser-start',kind);(P/'browser.pid').write_text(str(d['pid']));(P/'browser.kind').write_text(kind)
 b=None
 for _ in range(60):
  try:b,_=L.connect();break
  except (OSError,RuntimeError):time.sleep(.5)
 assert b is not None
 try:b.maximize()
 except Exception:pass
 time.sleep(3);b.navigate('about:blank');b.js("document.documentElement.style.background='rgb(255,0,254)';document.body.style.margin='0';document.body.style.height='100vh';return 0;");time.sleep(2.5);L.screen_png(P/'calibration.png')
 import numpy as np
 from PIL import Image
 a=np.asarray(Image.open(P/'calibration.png').convert('RGB')).astype(int);m=(abs(a[:,:,0]-255)<6)&(a[:,:,1]<6)&(abs(a[:,:,2]-254)<6);ys,xs=np.where(m.any(axis=1))[0],np.where(m.any(axis=0))[0];assert len(ys),'Browser not visible in guest'
 rect=[int(xs[0]),int(ys[0]),int(xs[-1]-xs[0]+1),int(ys[-1]-ys[0]+1)];solid=float(m[rect[1]:rect[1]+rect[3],rect[0]:rect[0]+rect[2]].mean());assert solid>.98,solid;info=b.js(L.INFO)
 (P/'viewport.json').write_text(json.dumps({'rect':rect,'solid':solid,'info':info,'screen':[a.shape[1],a.shape[0]],'desktop':DESKTOP,'kind':kind,'version':d['version'],'transport':'Browser and product in native guest; Marionette and QEMU VNC read over pinned SSH'},indent=1));print(json.dumps({'rect':rect,'solid':solid,'version':d['version']}),flush=True)
 b.cmd('WebDriver:DeleteSession',{});b.s.close()
L.browser_start=browser_start;L.browser_stop=lambda:print(json.dumps(remote('browser-stop')),flush=True)
