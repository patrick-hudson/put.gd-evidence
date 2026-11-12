from pathlib import Path
import sys,os,subprocess,json,time,hashlib,shutil
P=Path('/tmp/cp3');paths=[P/'runtime/putgd/session.sock'];e=dict(os.environ);cli=str(Path.home()/'putgd-lab/bin/putgd-cli')
def rpc(m,a={}):
 r=subprocess.run([cli,'--socket',str(paths[0]),m,json.dumps(a)],env=e,capture_output=True,text=True,timeout=75);v=json.loads(r.stdout)
 with open(P/'rpc.jsonl','a') as f:f.write(json.dumps({'time':time.time(),'method':m,'params':a,'reply':v})+chr(10))
 assert v['ok'],v
 return v['result']
rows=[json.loads(l) for l in (P/'rpc.jsonl').read_text().splitlines()];ident=next(v['reply']['result']['id'] for v in rows if v['method']=='scroll.prepare');v=rpc('scroll.inspect',{'id':ident});assert v['state']=='ready',v
class Owned:
 def __init__(self,arg):
  self.pid=None
  for p in Path('/proc').iterdir():
   if not p.name.isdigit():continue
   try:
    a=(p/'cmdline').read_bytes().split(bytes([0]));env=(p/'environ').read_bytes().split(bytes([0]))
    if arg.encode() in a and (arg.endswith('receiver3.py') or b'XDG_CONFIG_HOME=/tmp/cp3/c' in env):self.pid=int(p.name)
   except OSError:pass
  assert self.pid,arg
 def terminate(self):os.kill(self.pid,15)
 def wait(self,t):time.sleep(.2)
fixture=Owned('/home/lab/cap-ruler.py');server=Owned('/home/lab/cap-receiver3.py')
rpc('scroll.start',{'id':ident})
for _ in range(1800):
 v=rpc('scroll.inspect',{'id':ident})
 if v['state'] in ['done','failed','cancelled']:break
 time.sleep(.1)
sha=v.get('result',{}).get('sha256');assert sha,v
for _ in range(100):
 found=[f for f in (P/'archive').rglob('*.png') if hashlib.sha256(f.read_bytes()).hexdigest()==sha]
 if found:shutil.copyfile(found[0],P/'case/capture.png');break
 time.sleep(.1)
(P/'case/result.json').write_text(json.dumps({'capture':v},indent=2));sys.path.insert(0,'/home/lab');import scroll_run,argparse
ver=scroll_run.verify(P/'case/capture.png',argparse.Namespace(scale=1,height=2000,rows=600,first_pixel=0,header=0,footer=0,code_width=960,format='fixture',scrollbar=0));(P/'case/verification.json').write_text(json.dumps(ver,indent=2));fixture.terminate();fixture.wait(10);(P/'photo-ready').write_text('ready')
for _ in range(300):
 if (P/'release-upload').exists():break
 time.sleep(.1)
(P/'hold-upload').unlink();time.sleep(2);receipt=json.loads((P/'receiver-receipt.json').read_text());receipt['admittedPngSha256']=sha;receipt['loopbackPayloadEqualsPng']=receipt['pngSha256']==sha;(P/'case/upload-verification.json').write_text(json.dumps(receipt,indent=2));shutil.copyfile(P/'received.png',P/'case/received.png');shutil.copyfile(P/'received.multipart',P/'case/received.multipart');shutil.copyfile(P/'helper.log',P/'case/helper.log');op=rpc('operation.inspect',{'id':v['operationId']});(P/'case/upload-completion.json').write_text(json.dumps(op,indent=2));rpc('ui.quit');server.terminate();server.wait(10);assert ver['pass'] and receipt['loopbackPayloadEqualsPng'] and v['endReason']=='height_cap' and v['height']==2000;(P/'done').write_text('done');print('CAP PAYLOAD VERIFIED',flush=True)
