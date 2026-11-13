from pathlib import Path
import subprocess,json,os,time,unicodedata,collections,hashlib,signal
r=Path.home()/'work/ocr-final-1428';w=r/'candidate-busy-supplement';w.mkdir(mode=0o700);rt=Path('/tmp/f1428busy');rt.mkdir(mode=0o700);runtime=rt/'r';runtime.mkdir(mode=0o700);sock=runtime/'putgd/session.sock';assert len(str(sock).encode())<=107
prefix=r/'ubuntu24-candidate/usr';env={'HOME':str(Path.home()),'USER':'patrick','LOGNAME':'patrick','PATH':'/usr/bin:/bin','LANG':'C.UTF-8','QT_QPA_PLATFORM':'offscreen','XDG_RUNTIME_DIR':str(runtime),'XDG_CONFIG_HOME':str(w/'c'),'XDG_DATA_HOME':str(w/'d'),'XDG_STATE_HOME':str(w/'s'),'XDG_CACHE_HOME':str(w/'k')}
log=(w/'resident.log').open('x');app=subprocess.Popen([str(prefix/'bin/putgd'),'--background','-platform','offscreen'],env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);(w/'identity.json').write_text(json.dumps({'pid':app.pid,'socketBytes':len(str(sock).encode()),'candidate':'357210d2f1cb7b65f77166e34eb535d42e497fd0','scope':'offline fixed-file recognition only, no desktop pipeline proof'}))
def call(method,params):
 p=subprocess.run([str(prefix/'bin/putgd-cli'),'--socket',str(sock),'--params-stdin',method],input=json.dumps(params),env=env,capture_output=True,text=True,timeout=35);v=json.loads(p.stdout)
 if not v.get('ok'):raise RuntimeError(v.get('error',{}).get('code','missing_reply'))
 return v['result']
def recognize(image):
 op=call('text.recognize',{'source':'file','path':str(image),'copy':False})['operationId'];end=time.monotonic()+30
 while time.monotonic()<end:
  v=call('text.inspect',{'id':op})
  if v['state'] in ['completed','failed','cancelled']:
   if v['state']!='completed':raise RuntimeError(v.get('error',{}).get('code',v['state']))
   return v
  time.sleep(.03)
 call('text.cancel',{'id':op});raise RuntimeError('deadline')
def clean(s):
 return unicodedata.normalize('NFC',''.join('\n' if c in '\u2028\u2029' else c for c in s if (ord(c)>=32 or c in '\t\n') and not 127<=ord(c)<=159 and unicodedata.category(c)!='Cf'))
for _ in range(100):
 if sock.exists():break
 time.sleep(.05)
fixtures=r/'synthetic-final'
try:
 from PIL import Image,ImageOps
 manifest=json.loads((fixtures/'manifest.json').read_text());qr=[c for c in manifest['codes'] if c['format']=='qr'][:4];busy=Image.open(fixtures/'codes-multiple-busy.png').convert('RGB');placed=[]
 for i,c in enumerate(qr):
  path=fixtures/c['image'];code=Image.open(path).convert('RGB');x,y=100+i*300,300;box=[x,y,x+code.width,y+code.height];assert busy.crop(box).tobytes()==code.tobytes(),'source crop does not match generator placement'
  placed.append(dict(c,box=box,imageSha256=hashlib.sha256(path.read_bytes()).hexdigest()))
 truth={'reason':'Published working set omitted codes-multiple-busy.truth.json. Placements reconstructed from the stored manifest and original generator; all four crop byte arrays verified against unchanged PNGs before any frame was added.','codes':placed};(w/'reconstructed-truth.json').write_text(json.dumps(truth,indent=2))
 dark=next(c for c in placed if c['image'].endswith('-dark.png'));box=dark['box'];code=Image.open(fixtures/dark['image']).convert('RGB');busy.paste(ImageOps.expand(code,border=14,fill='black'),(box[0]-14,box[1]-14));framed=w/'codes-multiple-busy-framed.png';busy.save(framed);rows=[]
 for name,path in [('original',fixtures/'codes-multiple-busy.png'),('dark14pxFrame',framed)]:
  v=recognize(path);codes=v.get('codes',[]);slots=[]
  for found in codes:
   cx=sum(p[0] for p in found['quad'])/4;cy=sum(p[1] for p in found['quad'])/4
   slots.extend(i for i,item in enumerate(placed) if item['box'][0]<=cx<=item['box'][2] and item['box'][1]<=cy<=item['box'][3])
  rows.append({'case':name,'sourceSha256':hashlib.sha256(path.read_bytes()).hexdigest(),'recognitionJobs':1,'codeCount':len(codes),'codes':[dict(format=x['format'],kind=x['kind'],quad=x['quad'],textSha256=hashlib.sha256(x.get('text','').encode()).hexdigest()) for x in codes],'expected':4,'matchedSourceSlots':slots,'allFourExact':len(codes)==4 and sorted(slots)==[0,1,2,3] and all(x.get('text')=='https://example.invalid/corpus' for x in codes)})
 (w/'receipt.json').write_text(json.dumps({'candidate':'357210d2f1cb7b65f77166e34eb535d42e497fd0','rows':rows},indent=2));print(json.dumps(rows,indent=2))
finally:
 app.terminate();app.wait(timeout=10)
