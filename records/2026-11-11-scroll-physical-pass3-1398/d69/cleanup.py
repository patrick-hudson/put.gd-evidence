import pass2,json,os,time,subprocess
from pathlib import Path
P=pass2.P
try: print(pass2.rpc('ui.quit'))
except Exception as ex:print(type(ex).__name__)
time.sleep(3)
left=[]
for proc in Path('/proc').iterdir():
 if not proc.name.isdigit():continue
 try:
  if ('XDG_CONFIG_HOME='+str(P/'c')).encode() in (proc/'environ').read_bytes().split(b'\0') and (proc/'comm').read_text().startswith('putgd'):
   left.append({'pid':int(proc.name),'comm':(proc/'comm').read_text().strip()});os.kill(int(proc.name),15)
 except (FileNotFoundError,PermissionError,ProcessLookupError):pass
time.sleep(2)
(P/'cleanup.json').write_text(json.dumps({'terminatedOwned':left,'activeVT':subprocess.getoutput('cat /sys/class/tty/tty0/active'),'fgconsole':subprocess.getoutput('sudo -n fgconsole'),'session':subprocess.getoutput('loginctl list-sessions --no-legend | while read sid uid usr rest; do loginctl show-session "$sid" -p Id -p Active -p State -p VTNr -p Type; done')},indent=2))
print((P/'cleanup.json').read_text())
