set -eu
cd "$HOME/work/s5202"
python3 - <<'PY'
from pathlib import Path
import os,json,subprocess,shlex,hashlib
l=Path.home()/'work/s5202';ps=json.loads((l/'preflight.json').read_text())['processes'];v=next(p['env'] for p in ps if p['comm']=='cinnamon');(l/'session.env').write_text('\n'.join('export '+k+'='+shlex.quote(x) for k,x in v.items())+'\n');os.environ.update(v)
base={'xinput':subprocess.check_output(['xinput','--list','--long'],text=True),'pointer':subprocess.check_output(['xdotool','getmouselocation','--shell'],text=True),'packageStatus':subprocess.check_output(['dpkg-query','-s','putgd'],text=True)}
p=Path('/etc/apt/sources.list.d/putgd.sources');base['aptSourceExists']=p.exists()
if p.exists():
 (l/'apt-source-before.private').write_bytes(p.read_bytes());(l/'apt-source-before.private').chmod(0o600);base['aptSourceSha256']=hashlib.sha256(p.read_bytes()).hexdigest()
(l/'before-state.json').write_text(json.dumps(base,indent=2))
for label in ['a','b']:
 for n in ['config','data','cache','state','run','out']:(l/label/n).mkdir(parents=True,mode=0o700,exist_ok=True)
paths=[str(l/label/'run/putgd/session.sock') for label in ['a','b']]+[v['DBUS_SESSION_BUS_ADDRESS'].split('=',1)[1],'/tmp/.X11-unix/X0'];sizes={p:len(p.encode()) for p in paths};assert all(n<=107 for n in sizes.values());(l/'socket-paths.json').write_text(json.dumps(sizes,indent=2));print(json.dumps(sizes))
PY
