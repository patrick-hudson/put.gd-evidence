import json,time,subprocess
from pathlib import Path
def extra(r):
 out=r.receipt['supplement']={}
 # A real GNOME resize gesture. The application enforces its own minimum.
 r.cli('ui.show',{'view':'history'});time.sleep(1);r.input.chord(['alt','tab']);time.sleep(1);r.input.chord(['alt','f8'])
 r.input.chord(['left'])
 for i in range(200):r.input.chord(['right'])
 r.input.chord(['ret']);time.sleep(1)
 subprocess.run(['python3',r.args.rfb,str(r.args.rfb_port),str(r.root/'band-minimum.png')],check=True)
 print(json.dumps({'supplement':out}),flush=True)
