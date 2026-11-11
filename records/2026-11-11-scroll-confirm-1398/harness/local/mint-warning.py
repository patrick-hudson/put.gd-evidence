from pathlib import Path
import subprocess,time,json,os
import pass2 as p
P=p.P;p.setup();s=p.rpc('settings.get');p.rpc('settings.patch',{'patch':{'preferences':{'notifications':True}},'expectedRevision':s['metadata']['observedRevision']})
subprocess.run(['python3',str(P/'upload_setup.py')],check=True)
e=json.loads((P/'env.json').read_text());f=subprocess.Popen(['python3',str(P/'qt_fixture.py')],env=e,stdout=open(P/'warning-fixture.log','w'),stderr=subprocess.STDOUT)
try:
 time.sleep(3);p.capture('cap',60,2000)
 import rfb
 rfb.RFB(5900).screenshot(P/'warning-during-upload.png')
 time.sleep(10)
finally:f.terminate();f.wait(10)
subprocess.run(['python3',str(P/'finish.py'),'m74'],check=True)
