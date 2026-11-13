from pathlib import Path
import os,subprocess,time,json,socket,struct,signal,hashlib
from PIL import Image,ImageDraw,ImageFont
from text_proof import session_environment
r=Path.home()/'work/ocr-final-1428';w=Path.home()/'work/f1428unicode';w.mkdir(mode=0o700)
base,_=session_environment(['cinnamon']);base.pop('WAYLAND_DISPLAY',None)
base['PUTGD_TEXT_LAB_SESSION']='final1428-m74-g4'
source=['Grüße aus Köln.','Die Füße stehen neben großen Öfen.']
im=Image.new('RGB',(1200,240),'white');d=ImageDraw.Draw(im);font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',32)
for i,line in enumerate(source):d.text((30,25+70*i),line,font=font,fill='black')
image=w/'german-two-lines.png';im.save(image);rows=[];cli=str(r/'ubuntu24-candidate/usr/bin/putgd-cli')
for kind in ['native','appimage']:
 out=w/kind;out.mkdir(mode=0o700);runtime=Path('/tmp/f1428unicode'+('n' if kind=='native' else 'a'));runtime.mkdir(mode=0o700);sock=runtime/'putgd/session.sock';assert len(str(sock).encode())<=107
 env=base|dict(XDG_RUNTIME_DIR=str(runtime),XDG_CONFIG_HOME=str(out/'c'),XDG_DATA_HOME=str(out/'d'),XDG_STATE_HOME=str(out/'s'),XDG_CACHE_HOME=str(out/'k'))
 (out/'socket-preflight.json').write_text(json.dumps({'path':str(sock),'utf8Bytes':len(str(sock).encode())}))
 binary=r/'ubuntu24-candidate/usr/bin/putgd' if kind=='native' else next(r.glob('*.AppImage'));app=None;resident=None
 def call(method,params={}):
  p=subprocess.run([cli,'--socket',str(sock),'--params-stdin',method],input=json.dumps(params),env=env,capture_output=True,text=True,timeout=30);v=json.loads(p.stdout);assert v.get('ok'),v.get('error');return v['result']
 def paste(primary=False):
  p=subprocess.run(['xclip','-selection','primary' if primary else 'clipboard','-o'],env=base,capture_output=True,timeout=10);return p.returncode,p.stdout
 def recognize(copy):
  op=call('text.recognize',{'source':'file','path':str(image),'copy':copy,'languages':['deu']})['operationId'];end=time.monotonic()+30
  while time.monotonic()<end:
   v=call('text.inspect',{'id':op})
   if v['state'] in ['completed','failed','cancelled']:return op,v
   time.sleep(.03)
  raise RuntimeError('recognition deadline')
 try:
  primary=paste(True);assert primary==(0,b'SYNTHETIC PRIMARY 1428'), 'expected seeded PRIMARY not present'
  app=subprocess.Popen([str(binary),'--background'],env=env,stdout=(out/'resident.log').open('x'),stderr=subprocess.STDOUT);end=time.monotonic()+20
  while not sock.exists() and time.monotonic()<end:time.sleep(.05)
  with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as peer:peer.connect(str(sock));resident,uid,_=struct.unpack('3i',peer.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12))
  assert uid==os.getuid();exe=os.readlink('/proc/'+str(resident)+'/exe');assert (kind=='native' or '/.mount_' in exe)
  admissionId,v=recognize(False);text=v.get('text','');admitted=v['state']=='completed' and '\n' in text and any(ord(c)>127 for c in text);assert admitted,'multiline non-ASCII fixture was not admitted'
  op,v=recognize(True);data=v.get('text','').encode();exact=paste()==(0,data);met=v['state']=='completed' and v.get('copyStatus')=='copied' and exact and '\n' in v.get('text','') and any(b>=128 for b in data) and paste(True)==primary
  row={'kind':kind,'status':'met' if met else 'missed','admissionOperation':admissionId,'operationId':op,'languages':['deu'],'completed':v['state']=='completed','copyStatus':v.get('copyStatus'),'multiline':'\n' in v.get('text',''),'nonASCII':any(b>=128 for b in data),'independentByteExactPaste':exact,'PRIMARYUnchanged':paste(True)==primary,'recognizedSyntheticText':v.get('text'),'textSha256':hashlib.sha256(data).hexdigest(),'characterCount':v.get('characterCount'),'residentPid':resident,'actualExecutable':exe}
 except Exception as e:row={'kind':kind,'status':'not_run','reason':str(e)}
 finally:
  if resident and Path('/proc',str(resident)).exists():os.kill(resident,signal.SIGTERM)
  if app:app.wait(timeout=15)
 rows.append(row);(w/'receipt.json').write_text(json.dumps({'candidate':'357210d2f1cb7b65f77166e34eb535d42e497fd0','source':source,'fontPixels':32,'sourceSha256':hashlib.sha256(image.read_bytes()).hexdigest(),'rows':rows},indent=2));print(kind,row['status'],flush=True)
