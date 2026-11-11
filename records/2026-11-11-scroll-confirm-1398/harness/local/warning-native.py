import pass2 as p,json,subprocess,time,os,shutil
P=p.P;e=json.loads((P/'env.json').read_text());s=P/'supplemental';s.mkdir(exist_ok=True)
f=subprocess.Popen(['python3',str(P/'qt_fixture.py')],env=e,stdout=open(s/'warning-fixture.log','w'),stderr=subprocess.STDOUT)
try:time.sleep(3);p.capture('cap-visual-probe',60,2000)
finally:f.terminate();f.wait(15)
time.sleep(2)
import rfb
rfb.RFB(5901 if os.uname().nodename=='fedora' else 5900).screenshot(s/'warning-visible.png')
(P/'cap-visual-probe').rename(s/'cap-visual-probe')
