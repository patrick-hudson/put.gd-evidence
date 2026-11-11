import pass2 as p,subprocess,time,json,os
P=p.P;e=json.loads((P/'env.json').read_text());e['SC_Y']='40'
subprocess.run(['python3',str(P/'cinnamon_scale.py'),'snapshot'],check=True)
try:
 subprocess.run(['python3',str(P/'cinnamon_scale.py'),'fractional'],check=True)
 subprocess.run(['python3',str(P/'cinnamon_scale.py'),'scale','1.5'],check=True)
 f=subprocess.Popen(['python3',str(P/'qt_fixture.py')],env=e,stdout=open(P/'scale-retry-fixture.log','w'),stderr=subprocess.STDOUT)
 try:
  time.sleep(3);orig=p.rpc
  def rpc(m,args={}):
   if m=='scroll.prepare':args=dict(args,rect=[200,80,1920,1200])
   return orig(m,args)
  p.rpc=rpc;p.capture('scale150-correct',scale=2)
 finally:f.terminate();f.wait(10)
finally:subprocess.run(['python3',str(P/'cinnamon_scale.py'),'restore'],check=True)
