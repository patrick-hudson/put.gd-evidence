from text_proof import session_environment
from pathlib import Path
from rfb import RFB
import subprocess,json,tempfile,time,os,signal,hashlib
A=Path('/home/lab/ai2/squashfs-root');E,_=session_environment(['gsd-power']);out=[]
fixture=subprocess.Popen(['python3','/home/lab/fixture.py'],env=E,start_new_session=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
def run(name,target,expected):
 root=Path(tempfile.mkdtemp(prefix='un-',dir='/tmp'));rt=root/'rt';rt.mkdir(mode=0o700);sock=rt/'putgd/session.sock';assert len(str(sock).encode())<=107
 e=dict(E,XDG_RUNTIME_DIR=str(rt),XDG_CONFIG_HOME=str(root/'config'),XDG_DATA_HOME=str(root/'data'),XDG_STATE_HOME=str(root/'state'),XDG_CACHE_HOME=str(root/'cache'),APPIMAGE='/home/lab/candidate.AppImage',APPDIR=str(A))
 if not E.get('WAYLAND_DISPLAY','').startswith('/'):e['WAYLAND_DISPLAY']=str(Path(E['XDG_RUNTIME_DIR'])/E['WAYLAND_DISPLAY'])
 c=dict(e,LD_LIBRARY_PATH=str(A/'usr/lib')+':'+str(A/'usr/lib/putgd'))
 def cli(method,p={}):
  q=subprocess.run([str(A/'usr/bin/putgd-cli'),'--socket',str(sock),method,json.dumps(p)],env=c,capture_output=True,text=True,timeout=30);return json.loads(q.stdout)
 held=target.with_name(target.name+'.held-a1428');assert target.is_file() and not held.exists();before=hashlib.sha256(target.read_bytes()).hexdigest();target.rename(held);p=None
 row={'case':name,'held':str(target),'sha256Before':before,'socket':str(sock),'socketBytes':len(str(sock).encode())}
 try:
  p=subprocess.Popen([str(A/'AppRun'),'--background'],env=e,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True)
  for i in range(100):
   if sock.exists():break
   time.sleep(.1)
  time.sleep(2);v=RFB(5989);v.click(640,400);v.close()
  sentinel='unavailable-sentinel-'+name;subprocess.run(['wl-copy'],input=sentinel.encode(),env=E,check=True,timeout=10)
  row['capability']=cli('capabilities')['result']['text'];start=cli('text.recognize',{'source':'file','path':'/home/lab/text.png','copy':True});row['start']=start
  error=start.get('error',{}).get('code')
  if start['ok']:
   ident=start['result']['operationId']
   for i in range(100):
    state=cli('text.inspect',{'id':ident})['result']
    if state.get('state') in ('completed','failed','cancelled'):break
    time.sleep(.1)
   row['terminal']=state;error=state.get('error',{}).get('code')
  row['paste']=subprocess.check_output(['wl-paste','-n'],env=E,timeout=10).decode();row['helpers']=subprocess.run(['pgrep','-x','putgd-ocr'],capture_output=True,text=True).stdout.split();row['passed']=error==expected and row['paste']==sentinel and not row['helpers']
 finally:
  try:cli('ui.quit')
  except Exception:pass
  time.sleep(1)
  if p and p.poll() is None:os.killpg(p.pid,signal.SIGTERM)
  held.rename(target);row['sha256Restored']=hashlib.sha256(target.read_bytes()).hexdigest();row['restored']=row['sha256Restored']==before
 out.append(row);print(json.dumps(row),flush=True)
try:
 run('helper-missing',A/'usr/bin/putgd-ocr','text_helper_missing')
 run('english-missing',A/'usr/share/putgd/tessdata/eng.traineddata','engine_unavailable')
finally:
 if fixture.poll() is None:os.killpg(fixture.pid,signal.SIGTERM)
 Path('/home/lab/unavailable-receipt.json').write_text(json.dumps(out,indent=1))
