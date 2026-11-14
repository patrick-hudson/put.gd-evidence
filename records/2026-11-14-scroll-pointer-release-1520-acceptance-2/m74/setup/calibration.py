from pathlib import Path
from trial import cursorpos,flat
import subprocess,time,json
l=Path.home()/'work/s5202';p=subprocess.Popen(['sudo','-n','python3',str(l/'umouse.py')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True);assert p.stdout.readline().startswith('ready')
try:
 flat();subprocess.run(['xdotool','mousemove','960','540'],check=True);time.sleep(.1);a=cursorpos();p.stdin.write('m 100 0\n');p.stdin.flush();time.sleep(.15);b=cursorpos();v={'before':a,'after':b,'relativeUnits':[100,0],'flatProperties':subprocess.check_output(['xinput','list-props','putgd-lab relative mouse'],text=True)};assert b==[a[0]+100,a[1]],v;(l/'calibration.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
finally:p.stdin.write('q\n');p.stdin.flush();p.wait(5)
