import os,subprocess,time,json
from pathlib import Path
import accept as A
P=Path.cwd();assert len(json.loads((P/'main-process-results.json').read_text()))==10;assert not A.remote('helper-pids')
(P/'post-master.json').write_text(json.dumps({'pid':os.getpid(),'start':time.time()},indent=1));rows=[]
steps=[('pointer20',['pause-relative.py','--only-pointer'],{}),('functional',['extra-relative.py'],{}),('mixed-safe',['mixed-focused.py'],{}),('native-auto-recovery',['auto-native-recovery.py'],{}),('inside-whole',['pages-relative.py','firefox','wiki','user,auto'],{'LAB_RECT':'0,0,1920,1080','LAB_TAG':'inside'}),('25-notch',['pages-relative.py','firefox','wiki','user'],{'LAB_JUMP':'1','LAB_TAG':'jump'}),('audit',['audit-controls.py'],{}),('keyboard-focus',['keyboard-capture-probe.py'],{}),('blank-crossing-and-race',['blank-and-race-supplement.py'],{}),('user-js-recovery',['user-script-recovery.py'],{}),('auto-js-recovery',['auto-script-recovery.py'],{})]
for label,args,overrides in steps:
 assert not A.remote('helper-pids'),'An earlier capture is still running before '+label
 with(P/(label+'.log')).open('w')as f:r=subprocess.run(['python3','-u',*args],env=dict(os.environ,**overrides),stdout=f,stderr=subprocess.STDOUT)
 row={'label':label,'args':args,'environmentOverrides':overrides,'exit':r.returncode,'finished':time.time()};rows.append(row);(P/'functional-process-results.json').write_text(json.dumps(rows,indent=1));print(json.dumps(row),flush=True)
 assert not A.remote('helper-pids'),'A capture did not clean up after '+label
