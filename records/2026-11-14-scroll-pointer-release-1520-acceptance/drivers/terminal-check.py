import os,sys,time,subprocess,json,struct
from pathlib import Path
from trial import Rfb,cli
l=Path.home()/'work/s1520';d=l/'a';c=str(l/'bin/cli-a');port=int(os.environ.get('VNC','5900'));r=None
if 'Budgie' in os.environ.get('XDG_CURRENT_DESKTOP',''):
 from geometry import output
 r=output()
else:r=Rfb(port)
if any(x in os.environ.get('XDG_CURRENT_DESKTOP','') for x in ['Hyprland','Budgie']):
 from localinput import Pointer
 r=Pointer(r)
s=cli(c,'scroll.prepare',{'rect':[470,200,980,720]})['result']['id'];cli(c,'scroll.start',{'id':s});time.sleep(4)
r.pointer(960,540);time.sleep(1)
v=cli(c,'scroll.inspect',{'id':s});json.dump(v,open(d/'terminal-paused.json','w'));print('paused',v,flush=True)
# Open a native terminal; the compositor places it. Coordinator clicks its visible body.
term=sys.argv[1]
args=[term,'-e','python3',str(l/'terminal-witness.py')]
p=subprocess.Popen(args,stdout=open(d/'terminal-launch.log','w'),stderr=subprocess.STDOUT,start_new_session=True)
(d/'terminal.pid').write_text(str(p.pid));(d/'terminal-session-id').write_text(s)
print('terminal pid',p.pid,flush=True)
