# Run only while our own browser page is already open, with no capture active.
import accept as A,json,threading,time
from pathlib import Path
P=A.P
sid=A.rpc('scroll.prepare',{'rect':[240,200,1440,820],'driver':'user'})['id'];A.rpc('scroll.start',{'id':sid});time.sleep(.5)
result={};thread=threading.Thread(target=lambda:result.update(stop=A.rpc('scroll.stop',{'id':sid})));thread.start()
for _ in range(100):
 v=A.rpc('scroll.inspect',{'id':sid})
 if v.get('state') in ['finishing','done']:break
 time.sleep(.001)
try:result['toggle']=A.rpc('scroll.autoScroll',{'id':sid,'on':True})
except Exception as e:result['toggleError']=str(e)
thread.join();result['during']=v;result['after']=A.rpc('scroll.inspect',{'id':sid});(P/'toggle-stop-race.json').write_text(json.dumps(result,indent=1));print(json.dumps(result))
