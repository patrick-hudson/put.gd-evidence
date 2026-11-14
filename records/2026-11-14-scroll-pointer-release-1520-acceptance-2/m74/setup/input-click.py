from pathlib import Path
from trial import flat,cursorpos,steer_command
import sys,subprocess,time,json
l=Path.home()/'work/s5202';target=[int(sys.argv[1]),int(sys.argv[2])];m=subprocess.Popen(['sudo','-n','python3',str(l/'umouse.py')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True);assert m.stdout.readline().startswith('ready')
try:
 flat()
 for _ in range(600):
  at=cursorpos();ex,ey=target[0]-at[0],target[1]-at[1]
  if abs(ex)<=2 and abs(ey)<=2:break
  m.stdin.write(steer_command(ex,ey,6));m.stdin.flush();time.sleep(.01)
 else:raise RuntimeError('pointer did not arrive')
 print(json.dumps({'target':target,'at':cursorpos()}),flush=True)
 if len(sys.argv)<4 or sys.argv[3]!='move':m.stdin.write('d\n');m.stdin.flush();time.sleep(.08);m.stdin.write('u\n');m.stdin.flush();time.sleep(.1)
finally:m.stdin.write('q\n');m.stdin.flush();m.wait(5)
