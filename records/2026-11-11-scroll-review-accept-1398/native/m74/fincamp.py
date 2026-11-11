import pass2 as p,subprocess,json,time,sys,traceback
P=p.P;host=sys.argv[1]
def run(*a):
 r=subprocess.run(['python3',*a],cwd=P,stdout=open(P/('-'.join(a)+'.console'),'w'),stderr=subprocess.STDOUT);print(a,r.returncode,flush=True)
for kind,n in [('plain',5),('firefox',5),('qtfull',2),('qtnarrowfull',2),('gtkfull',2),('gtknarrowfull',2),('long',1),('race',3)]:
 try:p.batch(kind,n)
 except Exception:traceback.print_exc()
run('extras3.py','mint')
run('special.py','stop2')
run('upload_setup.py')
e=json.loads((P/'env.json').read_text());f=subprocess.Popen(['python3',str(P/'qt_fixture.py'),'--rows','600'],env=e,stdout=open(P/'capflow-fixture.log','w'),stderr=subprocess.STDOUT)
try:
 time.sleep(3);p.capture('cap-final',600,2000);p.capture('postcap-final',600,40000,immediate=True)
finally:f.terminate();f.wait(10)
run('scale3.py',host)
run('special.py','user')
(P/'final-complete').write_text('done')
