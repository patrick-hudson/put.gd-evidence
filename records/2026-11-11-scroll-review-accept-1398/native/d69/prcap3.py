import pass2 as p,subprocess,json,time,sys,rfb
P=p.P;e=json.loads((P/'env.json').read_text());f=subprocess.Popen(['python3',str(P/'qt_fixture.py')],env=e,stdout=open(P/'prcap-fixture.log','w'),stderr=subprocess.STDOUT)
try:
 time.sleep(3);p.capture('cap-pr',maxh=2000)
 v=rfb.RFB(5901 if sys.argv[1]=='f44' else 5900)
 for i in range(4):v.screenshot(P/('pr-cap-%d.png'%i));time.sleep(.4)
finally:f.terminate();f.wait(10)
