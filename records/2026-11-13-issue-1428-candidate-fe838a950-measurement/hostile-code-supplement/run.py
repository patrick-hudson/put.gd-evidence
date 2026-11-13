from pathlib import Path
import subprocess,json,os,time,hashlib,unicodedata
r=Path.home()/'work/ocr-corpus-1428';w=r/'candidate-hostile-code-supplement';w.mkdir(mode=0o700);rt=Path('/tmp/i8hc1428');rt.mkdir(mode=0o700);runtime=rt/'r';runtime.mkdir(mode=0o700);sock=runtime/'putgd/session.sock';assert len(str(sock).encode())<=107;prefix=r/'debian-candidate/usr';env=dict(HOME=str(Path.home()),USER='patrick',LOGNAME='patrick',PATH='/usr/bin:/bin',LANG='C.UTF-8',QT_QPA_PLATFORM='offscreen',XDG_RUNTIME_DIR=str(runtime),XDG_CONFIG_HOME=str(w/'c'),XDG_DATA_HOME=str(w/'d'),XDG_STATE_HOME=str(w/'s'),XDG_CACHE_HOME=str(w/'k'));app=subprocess.Popen([str(prefix/'bin/putgd'),'--background','-platform','offscreen'],env=env,stdout=(w/'app.log').open('x'),stderr=subprocess.STDOUT);rows=[]
def call(m,p):
 v=json.loads(subprocess.run([str(prefix/'bin/putgd-cli'),'--socket',str(sock),'--params-stdin',m],input=json.dumps(p),env=env,capture_output=True,text=True,timeout=30).stdout)
 if not v.get('ok'):raise RuntimeError(v.get('error',{}).get('code','missing_reply'))
 return v['result']
try:
 end=time.monotonic()+20
 while not sock.exists() and time.monotonic()<end:time.sleep(.05)
 for name,sym in [('qr',58),('datamatrix',71),('aztec',92)]:
  payload='prefix\u202eevil\u202c\u200b\u200c\u200d\u2066suffix\u2069 Cafe\u0301\u2028tail';expected='prefixevilsuffix Café\ntail';raw=w/(name+'.bin');raw.write_bytes(payload.encode());image=w/(name+'.png');cmd=['zint','-b',str(sym),'--binary','--eci','26','--scale','3','--whitesp','4','-i',str(raw),'-o',str(image)];p=subprocess.run(cmd,capture_output=True);assert p.returncode==0;op=call('text.recognize',{'source':'file','path':str(image),'copy':False})['operationId'];end=time.monotonic()+30
  while time.monotonic()<end:
   v=call('text.inspect',{'id':op})
   if v['state'] in ['completed','failed','cancelled']:break
   time.sleep(.05)
  codes=v.get('codes',[]);rows.append({'format':name,'payload_hex':payload.encode().hex(),'expected_codepoints':list(map(ord,expected)),'imageSha256':hashlib.sha256(image.read_bytes()).hexdigest(),'generatorArgv':cmd,'state':v['state'],'matched':any(c.get('kind')=='text' and c.get('text')==expected for c in codes),'codes':[{'format':c['format'],'kind':c['kind'],'length':c['length'],'text_codepoints':list(map(ord,c.get('text','')))} for c in codes]});(w/'receipt.json').write_text(json.dumps({'candidate':'fe838a9502167672f3512e27c32c74cfcf6c84d1','scope':'Additional explicitly ECI26 UTF8 text codes without C0/C1; original mixed-control fixtures and their binary results remain unchanged','rows':rows},indent=2));print(name,rows[-1]['matched'],rows[-1]['codes'],flush=True)
finally:app.terminate();app.wait(timeout=10)
