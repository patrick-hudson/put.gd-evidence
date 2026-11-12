from pathlib import Path
import sys,json,os,time,subprocess,hashlib,numpy as np
from PIL import Image
P=Path('/home/patrick/work/sm2');sys.path.insert(0,str(P));import pass2 as p,fix6 as f,rfb,verify_text
assert (P/'r/putgd/session.sock').exists()
for q in Path('/proc').iterdir():
 if not q.name.isdigit():continue
 try:
  if (q/'comm').read_text().strip()=='putgd-ui' and ('XDG_CONFIG_HOME='+str(P/'c')).encode() in (q/'environ').read_bytes().split(bytes([0])):os.kill(int(q.name),15)
 except OSError:pass
time.sleep(2);original=p.rpc;os.environ['SC_TEXT_WIDTH']='600'
for i in range(2):
 name='qt600-final-'+str(i)
 def capture():
  def rpc(m,a={}):
   if m=='scroll.start':
    q=rfb.RFB(5900);q.screenshot(P/(name+'-ready.png'));q.sock.close();im=Image.open(P/(name+'-ready.png')).convert('RGB').crop((0,0,600,1080));im.save(P/(name+'-ready-region.png'));v=verify_text.verify(str(P/(name+'-ready-region.png')),1500);arr=np.array(im).astype('int16');tail=arr[:,400:];bg=np.median(tail.reshape(-1,3),axis=0);bad=int(np.any(np.abs(tail-bg)>12,2).sum());state={'visibleBands':v['lines'],'distinct':v['lines']-v['duplicates'],'rightBlankMismatch':bad,'fixtureLog':(P/'narrow-fixture.log').read_text()};(P/(name+'-readiness.json')).write_text(json.dumps(state,indent=2));assert 40<v['lines']<100 and bad==0,state
   return original(m,a)
  p.rpc=rpc
  try:return p.capture(name,60,60000,text=True)
  finally:p.rpc=original
 r=f.with_fixture('narrow',['python3',str(P/'native_text_fixture.py'),'qt','600','bottom'],capture,5);assert r.get('pass'),r
(P/'retry.done').write_text('done')
