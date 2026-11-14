import os,json,time,subprocess
from pathlib import Path
from trial import cli,Rfb
l=Path.home()/'work/s1520';label='a';c=str(l/'bin/cli-a');r=Rfb(int(os.environ.get('VNC','5900')))
subprocess.run(['firefox','--profile',str(l/'ff'),'https://en.wikipedia.org/wiki/Linux']);time.sleep(5)
s=cli(c,'scroll.prepare',{'rect':[470,200,980,720]})['result']['id'];cli(c,'scroll.start',{'id':s});print(s,flush=True);(l/'a/probe-id').write_text(s)
time.sleep(6)
subprocess.run(['python3',str(l/'rfbshot.py'),str(l/'a/running.png'),'--vnc',str(int(os.environ.get('VNC','5900')))])
r.pointer(960,540);time.sleep(1)
json.dump(cli(c,'scroll.inspect',{'id':s}),open(l/'a/probe-paused.json','w'))
subprocess.run(['python3',str(l/'rfbshot.py'),str(l/'a/paused.png'),'--vnc',str(int(os.environ.get('VNC','5900')))])
time.sleep(25)
cli(c,'scroll.cancel',{'id':s})
