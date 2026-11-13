from pathlib import Path
import subprocess,json,os,time,unicodedata,collections,hashlib,signal
r=Path.home()/'work/ocr-final-1428';w=r/'candidate-file-code-checks';w.mkdir(mode=0o700);rt=Path('/tmp/f14fc1428');rt.mkdir(mode=0o700);runtime=rt/'r';runtime.mkdir(mode=0o700);sock=runtime/'putgd/session.sock';assert len(str(sock).encode())<=107
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
fixtures=r/'synthetic-final';m=json.loads((fixtures/'manifest.json').read_text());result={'status':'incomplete','scope':'real candidate resident, offscreen fixed-file checks; no clipboard/desktop proof','codes':[],'hidden':[]};formats={'qr':'QRCode','micro':'MicroQRCode','datamatrix':'DataMatrix','aztec':'Aztec'}
try:
 result['capabilities']=call('capabilities',{}).get('text')
 for c in m['codes']:
  row={'imageSha256':hashlib.sha256((fixtures/c['image']).read_bytes()).hexdigest(),'image':c['image'],'format':c['format'],'version':c.get('version'),'modulePixels':c['module_pixels'],'payloadSha256':hashlib.sha256(bytes.fromhex(c['payload_hex'])).hexdigest(),'status':'not_run'}
  try:
   v=recognize(fixtures/c['image']);found=v['codes'];payload=bytes.fromhex(c['payload_hex']);expected=clean(payload.decode('utf8')) if c['kind']=='text' else None
   matched=[x for x in found if x['format']==formats[c['format']] and x['kind']==c['kind'] and (x.get('text')==expected if c['kind']=='text' else x.get('length')==len(payload) and 'text' not in x)]
   ordered=[(sum(p[1] for p in x['quad']),sum(p[0] for p in x['quad'])) for x in found]
   row.update(status='measured',matched=bool(matched),ordered=ordered==sorted(ordered),codes=[{'format':x['format'],'kind':x['kind'],'length':x['length'],'quad':x['quad'],'textSha256':hashlib.sha256(x.get('text','').encode()).hexdigest()} for x in found],truncated=v['truncated'],timings=v.get('timings'))
  except Exception as e:row['reason']=str(e)
  result['codes'].append(row);(w/'receipt.json').write_text(json.dumps(result,indent=2))
 for name in ['hidden-near-white','hidden-tiny','hostile']:
  row={'image':name,'status':'not_run'}
  try:
   v=recognize(fixtures/(name+'.png'));text=v.get('text','');illegal=[ord(c) for c in text if ((ord(c)<32 and c not in '\t\n') or 127<=ord(c)<=159 or unicodedata.category(c)=='Cf' and c not in '\u200c\u200d')];row.update(status='measured',characterCount=len(text),illegalCodepoints=illegal,excluded=name=='hostile' or not text,copyStatus=v.get('copyStatus'))
  except Exception as e:row['reason']=str(e)
  result['hidden'].append(row);(w/'receipt.json').write_text(json.dumps(result,indent=2))
 from PIL import Image,ImageOps
 supp=w/'framed';supp.mkdir();truth=json.loads((fixtures/'codes-multiple-busy.truth.json').read_text());busy=Image.open(fixtures/'codes-multiple-busy.png').convert('RGB')
 dark=next(c for c in truth['codes'] if c['image'].endswith('-dark.png'));box=dark['box'];code=Image.open(fixtures/dark['image']).convert('RGB');busy.paste(ImageOps.expand(code,border=14,fill='black'),(box[0]-14,box[1]-14));framed=supp/'codes-multiple-busy-framed.png';busy.save(framed)
 result['multipleBusy']=[]
 for name,path in [('original',fixtures/'codes-multiple-busy.png'),('dark14pxFrame',framed)]:
  v=recognize(path);codes=v.get('codes',[]);slots=[]
  for found in codes:
   cx=sum(p[0] for p in found['quad'])/4;cy=sum(p[1] for p in found['quad'])/4
   slots.extend(i for i,item in enumerate(truth['codes']) if item['box'][0]<=cx<=item['box'][2] and item['box'][1]<=cy<=item['box'][3])
  result['multipleBusy'].append({'case':name,'sourceSha256':hashlib.sha256(path.read_bytes()).hexdigest(),'recognitionJobs':1,'codeCount':len(codes),'codes':[dict(format=x['format'],kind=x['kind'],quad=x['quad'],textSha256=hashlib.sha256(x.get('text','').encode()).hexdigest()) for x in codes],'expected':4,'matchedSourceSlots':slots,'allFourExact':len(codes)==4 and sorted(slots)==[0,1,2,3] and all(x.get('text')=='https://example.invalid/corpus' for x in codes)})
 result['status']='complete';(w/'receipt.json').write_text(json.dumps(result,indent=2))
finally:
 app.terminate();app.wait(timeout=10)
