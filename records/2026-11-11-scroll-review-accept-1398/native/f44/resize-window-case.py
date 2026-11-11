import pass2 as p,subprocess,time,json,traceback
P=p.P;e=json.loads((P/'env.json').read_text());f=subprocess.Popen(['python3',str(P/'resize_window_fixture.py'),'--rows','600','--start','23400'],env=e,stdout=open(P/'resize-fixture.log','w'),stderr=subprocess.STDOUT)
try:
 time.sleep(1);p.capture('resize-window',600,40000)
finally:f.terminate();f.wait(10)
f=subprocess.Popen(['python3',str(P/'qt_fixture.py')],env=e,stdout=open(P/'after-resize-fixture.log','w'),stderr=subprocess.STDOUT)
try:time.sleep(3);p.capture('after-resize-window',60,40000)
finally:f.terminate();f.wait(10)
(P/'resize-window.done').write_text('done')
