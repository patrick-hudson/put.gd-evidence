from pathlib import Path
import subprocess,json,os,time,hashlib,collections
from PIL import Image,ImageDraw,ImageFont
r=Path.home()/'work/ocr-corpus-1428';w=r/'candidate-no-gap-seams';w.mkdir(mode=0o700);image=Image.new('RGB',(256,32700),'white');draw=ImageDraw.Draw(image);fontpath=Path('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf');font=ImageFont.truetype(str(fontpath),14);truth=[]
for index,y in enumerate(range(8,32700-24,20)):
 text='ALPHA BRAVO';draw.text((12,y),text,font=font,fill='black');truth.append({'index':index,'box':list(draw.textbbox((12,y),text,font=font)),'text_codepoints':list(map(ord,text))})
draw.rectangle((0,0,2,32699),fill='black');path=w/'no-gap.png';image.save(path);(w/'truth.json').write_text(json.dumps({'dimensions':[256,32700],'railPixels':3,'wordsPerLine':2,'fontPixels':14,'fontSha256':hashlib.sha256(fontpath.read_bytes()).hexdigest(),'lines':truth},indent=2));prefix=r/'candidate-appimage-extracted/squashfs-root/usr';rt=Path('/tmp/i8ng1428');rt.mkdir(mode=0o700);sock=rt/'putgd/session.sock';assert len(str(sock).encode())<=107;offscreen=next(prefix.rglob('platforms/libqoffscreen.so'));env=dict(HOME=str(Path.home()),USER='patrick',LOGNAME='patrick',PATH='/usr/bin:/bin',LANG='C.UTF-8',QT_QPA_PLATFORM='offscreen',QT_PLUGIN_PATH=str(offscreen.parent.parent),XDG_RUNTIME_DIR=str(rt),XDG_CONFIG_HOME=str(w/'c'),XDG_DATA_HOME=str(w/'d'),XDG_STATE_HOME=str(w/'s'),XDG_CACHE_HOME=str(w/'k'));cli=prefix/'bin/putgd-cli';app=subprocess.Popen([str(prefix/'bin/putgd'),'--background','-platform','offscreen'],env=env,stdout=(w/'app.log').open('x'),stderr=subprocess.STDOUT)
def call(m,p):
 q=subprocess.run([str(cli),'--socket',str(sock),'--params-stdin',m],input=json.dumps(p),env=env,capture_output=True,text=True,timeout=30);v=json.loads(q.stdout)
 if not v.get('ok'):raise RuntimeError(v.get('error',{}).get('code','missing_reply'))
 return v['result']
try:
 end=time.monotonic()+20
 while not sock.exists() and time.monotonic()<end:
  if app.poll() is not None:raise RuntimeError('resident exited')
  time.sleep(.05)
 caps=call('capabilities',{});op=call('text.recognize',{'source':'file','path':str(path),'copy':False})['operationId'];end=time.monotonic()+30
 while time.monotonic()<end:
  v=call('text.inspect',{'id':op})
  if v['state'] in ['completed','failed','cancelled']:break
  time.sleep(.05)
 groups=collections.defaultdict(list);outside=[];origin=(truth[0]['box'][1]+truth[0]['box'][3])/2
 for word in v.get('words',[]):
  x,y,width,height=word['rect'];center=y+height/2;index=round((center-origin)/20)
  if index<0 or index>=len(truth) or abs(center-(origin+20*index))>6:outside.append(word['rect'])
  else:groups[index].append((x,word['text']))
 missing=[i for i in range(len(truth)) if i not in groups];wrong=[{'line':i,'wordCount':len(words),'actual_codepoints':list(map(ord,' '.join(t for x,t in sorted(words))))} for i,words in groups.items() if ' '.join(t for x,t in sorted(words))!='ALPHA BRAVO'];receipt={'candidate':'fe838a9502167672f3512e27c32c74cfcf6c84d1','scope':'Supplemental true no-gap band case, real bundled helper through unpacked AppImage resident; fixed-file offscreen only. Word-box row mapping prevents a lost and duplicated line cancelling in a count.','imageSha256':hashlib.sha256(path.read_bytes()).hexdigest(),'dimensions':[256,32700],'expectedLines':len(truth),'wordsReceived':len(v.get('words',[])),'state':v['state'],'banded':v.get('banded'),'truncated':v.get('truncated'),'copyStatus':v.get('copyStatus'),'missingLines':missing,'wrongOrDuplicatedLines':wrong,'unmappedWordBoxes':outside,'completeSeamWitness':v['state']=='completed' and v.get('banded') and not v.get('truncated') and not missing and not wrong and not outside,'timings':v.get('timings'),'languageData':caps.get('text',{}).get('languages')};(w/'receipt.json').write_text(json.dumps(receipt,indent=2));print({k:x for k,x in receipt.items() if k not in ['wrongOrDuplicatedLines','missingLines','unmappedWordBoxes','languageData']},flush=True);print('missing',len(missing),'wrong',len(wrong),'outside',len(outside),flush=True)
finally:app.terminate();app.wait(timeout=10)
