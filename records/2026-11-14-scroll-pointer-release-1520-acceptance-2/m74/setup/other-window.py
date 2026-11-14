from pathlib import Path
from trial import cli,flat,cursorpos
import subprocess,time,json
l=Path.home()/'work/s5202';a=l/'a';c=str(l/'bin/cli-a');subprocess.run(['firefox','--profile',str(l/'ff'),'https://en.wikipedia.org/wiki/Linux'],check=True);time.sleep(5)
s=cli(c,'scroll.prepare',{'rect':[470,200,980,720]})['result']['id'];cli(c,'scroll.start',{'id':s});time.sleep(3)
m=subprocess.Popen(['sudo','-n','python3',str(l/'umouse.py')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True);assert m.stdout.readline().startswith('ready');flat();at=cursorpos();m.stdin.write(f'm {960-at[0]} {540-at[1]}\n');m.stdin.flush();time.sleep(.3);m.stdin.write('q\n');m.stdin.flush();m.wait(5)
v=cli(c,'scroll.inspect',{'id':s});assert v['result'].get('paused') and v['result'].get('pausedBy')=='pointer',v;(a/'terminal-paused.json').write_text(json.dumps(v,indent=2));(a/'terminal-session-id').write_text(s);(a/'terminal-offset.txt').write_text(str((a/'helper.log').stat().st_size))
p=subprocess.Popen(['xterm','-geometry','100x30+100+100','-e','python3',str(l/'terminal-witness.py')],stdout=open(a/'terminal-launch.log','w'),stderr=subprocess.STDOUT,start_new_session=True);(a/'terminal.pid').write_text(str(p.pid));time.sleep(2);subprocess.run(['python3',str(l/'rfbshot.py'),str(a/'terminal-open.png'),'--vnc','5900'],check=True);print('paused and terminal open',s,p.pid,flush=True)
