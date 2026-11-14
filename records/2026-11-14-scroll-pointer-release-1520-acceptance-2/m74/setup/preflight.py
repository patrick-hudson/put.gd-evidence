from pathlib import Path
import os,json,subprocess
l=Path.home()/'work/s5202';allow=['DISPLAY','XAUTHORITY','XDG_RUNTIME_DIR','DBUS_SESSION_BUS_ADDRESS','XDG_SESSION_TYPE','XDG_CURRENT_DESKTOP']
ps=[]
for p in Path('/proc').iterdir():
 if not p.name.isdigit():continue
 try:
  if p.stat().st_uid!=os.getuid():continue
  comm=(p/'comm').read_text().strip()
  if comm not in ['cinnamon','cinnamon-sessio','cinnamon-session','Xorg','X0tigervnc']:continue
  env=dict(v.split('=',1) for v in (p/'environ').read_bytes().decode().split('\0') if '=' in v);ps.append({'pid':int(p.name),'comm':comm,'env':{k:env[k] for k in allow if k in env}})
 except (FileNotFoundError,PermissionError):pass
v={'processes':ps,'package':subprocess.run(['dpkg-query','-W','-f=${db:Status-Abbrev} ${Version}\n','putgd'],capture_output=True,text=True).stdout,'cinnamon':subprocess.check_output(['cinnamon','--version'],text=True).strip(),'load':subprocess.check_output(['uptime'],text=True).strip()};(l/'preflight.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
