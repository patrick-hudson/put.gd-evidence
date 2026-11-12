from pathlib import Path
import os,time,subprocess,sys,json
P=Path('/home/patrick/work/s3a');h=sys.argv[1]
def controls_running():
 for q in Path('/proc').iterdir():
  if not q.name.isdigit():continue
  try:
   a=(q/'cmdline').read_bytes().split(bytes([0]))
   if len(a)>1 and a[1] in [b'controls7.py',str(P/'controls7.py').encode()] and (q/'cwd').resolve()==P:return True
  except OSError:pass
 return False
while controls_running():time.sleep(1)
for args in [['more-a.py'],['cancel-extras.py',h],['next-native.py',h],['user-row.py',h],['newcases.py','a','b','c'],['latecases.py'],['late-ruler.py'],['minimap-repeat.py','minimap'],['timer-case.py']]:
 name='suite-'+args[0]
 with (P/(name+'.console')).open('w') as log:r=subprocess.run(['python3',str(P/args[0]),*args[1:]],stdout=log,stderr=subprocess.STDOUT)
 print(args,r.returncode,flush=True)
(P/'native-rest.done').write_text('done')
