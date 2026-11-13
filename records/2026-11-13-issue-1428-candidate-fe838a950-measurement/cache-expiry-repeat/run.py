from pathlib import Path
import subprocess,json,os,time,hashlib
r=Path.home()/'work/ocr-corpus-1428';w=r/'candidate-cache-expiry-repeat';w.mkdir(mode=0o700);rt=Path('/tmp/i8ce1428');rt.mkdir(mode=0o700);sock=rt/'putgd/session.sock';assert len(str(sock).encode())<=107;prefix=r/'ubuntu24-candidate/usr';env=dict(HOME=str(Path.home()),USER='patrick',LOGNAME='patrick',PATH='/usr/bin:/bin',LANG='C.UTF-8',QT_QPA_PLATFORM='offscreen',XDG_RUNTIME_DIR=str(rt),XDG_CONFIG_HOME=str(w/'c'),XDG_DATA_HOME=str(w/'d'),XDG_STATE_HOME=str(w/'s'),XDG_CACHE_HOME=str(w/'k'));app=subprocess.Popen([str(prefix/'bin/putgd'),'--background','-platform','offscreen'],env=env,stdout=(w/'app.log').open('x'),stderr=subprocess.STDOUT)
def call(m,p):
 v=json.loads(subprocess.run([str(prefix/'bin/putgd-cli'),'--socket',str(sock),'--params-stdin',m],input=json.dumps(p),env=env,capture_output=True,text=True,timeout=30).stdout)
 if not v.get('ok'):raise RuntimeError(v.get('error',{}).get('code','missing_reply'))
 return v['result']
try:
 end=time.monotonic()+20
 while not sock.exists() and time.monotonic()<end:time.sleep(.05)
 op=call('text.recognize',{'source':'file','path':str(r/'synthetic-final/limit-24mp.png'),'copy':False})['operationId'];end=time.monotonic()+30
 while time.monotonic()<end:
  v=call('text.inspect',{'id':op})
  if v['state'] in ['completed','failed','cancelled']:break
  time.sleep(.03)
 assert v['state']=='completed' and v.get('text');start=time.monotonic();rows=[]
 while time.monotonic()-start<128:
  age=time.monotonic()-start
  if age<118:time.sleep(min(1,118-age));continue
  q=time.monotonic();v=call('text.inspect',{'id':op});rows.append({'elapsedStart':q-start,'elapsedEnd':time.monotonic()-start,'expired':v.get('resultExpired'),'textPresent':'text' in v});(w/'receipt.json').write_text(json.dumps({'candidate':'fe838a9502167672f3512e27c32c74cfcf6c84d1','scope':'Additional offscreen native Qt6.4 cache-expiry observation, not a physical memory or latency acceptance replacement. Clock starts after observing completion; cache was stored no later than that. Original physical120.002s observation retained.','operationId':op,'rows':rows},indent=2))
  if v.get('resultExpired'):break
  time.sleep(.1)
 print('CACHE EXPIRY',rows[-1],flush=True)
finally:app.terminate();app.wait(timeout=10)
