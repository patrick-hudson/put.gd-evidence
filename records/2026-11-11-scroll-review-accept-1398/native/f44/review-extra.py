import pass2 as p,json,time,subprocess,sys,threading,traceback,hashlib
from pathlib import Path
P=p.P;h=sys.argv[1];e=json.loads((P/'env.json').read_text())
def fixture(args,fn):
 f=subprocess.Popen(['python3',str(P/'review_fixture.py'),*args],env=e,stdout=open(P/'extra-fixture.log','a'),stderr=subprocess.STDOUT)
 try:time.sleep(3);fn()
 finally:f.terminate();f.wait(15)
def cancel(phase,i):
 d=P/('cancel-'+phase+'-'+str(i));d.mkdir();off=(P/'helper.log').stat().st_size
 v=p.rpc('scroll.prepare',{'rect':[100,200,960,600]});ident=v['id']
 while v['state']!='ready':time.sleep(.05);v=p.rpc('scroll.inspect',{'id':ident})
 replies={};original=p.rpc
 def send(m):
  try:replies[m]=original('scroll.'+m,{'id':ident})
  except Exception as ex:replies[m]={'exception':str(ex)}
 if phase=='stop':send('start');time.sleep(.2)
 t=threading.Thread(target=send,args=(phase,));t.start();time.sleep(.001);send('cancel');t.join(75)
 replies['inspect']=p.rpc('scroll.inspect',{'id':ident});time.sleep(.4)
 replies['shell']=subprocess.getoutput('pgrep -x gnome-shell');(d/'result.json').write_text(json.dumps(replies,indent=2));(d/'helper.log').write_bytes((P/'helper.log').read_bytes()[off:])
 assert replies['inspect']['state']=='cancelled',replies
try:
 for i in range(2):fixture(['--rows','600','--start','12000','--switch'],lambda:p.capture('switch-'+str(i),600,40000))
 for cap in ([20,2000] if h in ['m74','d69'] else []):fixture(['--rows','600','--sticky'],lambda:p.capture('sticky-'+str(cap),600,cap,header=40,footer=40))
 fixture(['--rows','600'],lambda:[cancel(phase,i) for phase in ['start','stop'] for i in range(3 if h in ['f44','d69'] else 1)])
 fixture(['--rows','60'],lambda:p.capture('after-cancels',60,40000))
 (P/'extra.done').write_text('done')
except Exception:(P/'extra.error').write_text(traceback.format_exc());raise
