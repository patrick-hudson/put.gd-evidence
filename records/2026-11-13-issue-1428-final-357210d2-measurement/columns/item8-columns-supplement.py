from pathlib import Path
import subprocess,json,os,time,hashlib,collections
from PIL import Image,ImageDraw,ImageFont
r=Path.home()/'work/ocr-final-1428';w=r/'candidate-columns-supplement';w.mkdir(mode=0o700);im=Image.new('RGB',(1200,18000),'white');d=ImageDraw.Draw(im);font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf',18);truth=[]
for i,y in enumerate(range(12,17900,400)):
 for column,x in [('LEFT',24),('RIGHT',680)]:
  text=f'{column} LINE {i:03}';d.text((x,y),text,font=font,fill='black');truth.append({'column':column,'row':i,'text':text,'box':d.textbbox((x,y),text,font=font)})
path=w/'columns.png';im.save(path);(w/'truth.json').write_text(json.dumps(truth,indent=2));prefix=r/'ubuntu24-candidate/usr';rt=Path('/tmp/f14tc1428');rt.mkdir(mode=0o700);sock=rt/'putgd/session.sock';assert len(str(sock).encode())<=107;env=dict(HOME=str(Path.home()),USER='patrick',LOGNAME='patrick',PATH='/usr/bin:/bin',LANG='C.UTF-8',QT_QPA_PLATFORM='offscreen',XDG_RUNTIME_DIR=str(rt),XDG_CONFIG_HOME=str(w/'c'),XDG_DATA_HOME=str(w/'d'),XDG_STATE_HOME=str(w/'s'),XDG_CACHE_HOME=str(w/'k'));p=subprocess.Popen([str(prefix/'bin/putgd'),'--background','-platform','offscreen'],env=env,stdout=(w/'app.log').open('x'),stderr=subprocess.STDOUT)
def call(m,q):
 v=json.loads(subprocess.run([str(prefix/'bin/putgd-cli'),'--socket',str(sock),'--params-stdin',m],input=json.dumps(q),env=env,capture_output=True,text=True,timeout=30).stdout)
 if not v.get('ok'):raise RuntimeError(v.get('error',{}).get('code'))
 return v['result']
try:
 end=time.monotonic()+20
 while not sock.exists() and time.monotonic()<end:time.sleep(.05)
 op=call('text.recognize',{'source':'file','path':str(path),'copy':False})['operationId'];end=time.monotonic()+30
 while time.monotonic()<end:
  v=call('text.inspect',{'id':op})
  if v['state'] in ['completed','failed','cancelled']:break
  time.sleep(.05)
 groups=collections.defaultdict(list);sequence=[]
 for word in v.get('words',[]):
  x,y,width,height=word['rect'];column='LEFT' if x<600 else 'RIGHT';row=round((y+height/2-29)/400);key=(column,row)
  if key not in groups:sequence.append(key)
  groups[key].append((x,word['text']))
 mismatches=[{'column':t['column'],'row':t['row'],'actual':' '.join(z[1] for z in sorted(groups.get((t['column'],t['row']),[]))),'expected':t['text']} for t in truth if ' '.join(z[1] for z in sorted(groups.get((t['column'],t['row']),[])))!=t['text']]
 receipt={'candidate':'357210d2f1cb7b65f77166e34eb535d42e497fd0','scope':'Supplementary sparse tall two-column page, real native helper; original dense truncated receipt retained. Ordering is recorded, not inferred from banded alone.','sourceSha256':hashlib.sha256(path.read_bytes()).hexdigest(),'dimensions':[1200,18000],'fontPixels':18,'expectedLines':len(truth),'state':v['state'],'banded':v.get('banded'),'truncated':v.get('truncated'),'timings':v.get('timings'),'sequence':sequence,'mismatches':mismatches,'text':v.get('text','')};(w/'receipt.json').write_text(json.dumps(receipt,indent=2));print('columns',v['state'],v.get('banded'),v.get('truncated'),len(mismatches),sequence,flush=True)
finally:p.terminate();p.wait(timeout=10)
