import os,sys,json,time,subprocess,tempfile,pathlib,sqlite3
from PIL import Image,ImageGrab
src=pathlib.Path.cwd(); build=src/'build/dev'; root=pathlib.Path(tempfile.mkdtemp(prefix='sc1376-',dir='/tmp')); os.chmod(root,0o700)
env=os.environ.copy();env.update(XDG_RUNTIME_DIR=str(root/'r'),XDG_CONFIG_HOME=str(root/'c'),XDG_DATA_HOME=str(root/'d'),XDG_STATE_HOME=str(root/'s'),XDG_CACHE_HOME=str(root/'cache'),XDG_SESSION_TYPE='x11',XDG_CURRENT_DESKTOP='putgd-scroll-fixture',QT_QPA_PLATFORM='xcb')
env['PUTGD_RECORD_DEBUG_LOG']=str(root/'helper-debug.log');env.pop('WAYLAND_DISPLAY',None);(root/'r').mkdir(mode=0o700);sock=root/'r/putgd/session.sock'
subprocess.run([sys.executable,'tools/diagnostics/check_socket_paths.py','--socket',str(sock)],check=True)
print('EVIDENCE',root,flush=True)
(root/'build-info.json').write_text(subprocess.check_output([str(build/'putgd'),'--version-json'],text=True))
log=(root/'resident.log').open('w');resident=subprocess.Popen([str(build/'putgd'),'--background'],env=env,stdout=log,stderr=log)
fixture=None
transcript=[]
def call(method,p={}):
 r=subprocess.run([str(build/'putgd-cli'),'--socket',str(sock),method,json.dumps(p)],env=env,capture_output=True,text=True,timeout=50);v=json.loads(r.stdout);transcript.append([method,p,v]);(root/'transcript.json').write_text(json.dumps(transcript,indent=2));assert v['ok'],v;return v['result']
def wait(f,seconds=40):
 end=time.monotonic()+seconds
 while time.monotonic()<end:
  v=f()
  if v:return v
  time.sleep(.1)
 raise AssertionError('timeout')
def page():
 global fixture
 if fixture:fixture.terminate();fixture.wait()
 fixture=subprocess.Popen([str(build/'test_scroll_page_fixture'),'--rows','80'],env=env,stdout=(root/'fixture.log').open('w'),stderr=subprocess.STDOUT);time.sleep(.6)
def pattern(row,line):
 if line<2:return 65535
 if line<30:return row
 x=(row*2654435761+line*40503+0x9e3779b9)&0xffffffff;x^=x>>15;x=x*0x2c1b3c6d&0xffffffff;x^=x>>12;x=x*0x297a2d39&0xffffffff;x^=x>>15;b=x&65535
 return (0x5a5a^line) if b in (0,65535) else b
def verify(path,height):
 im=Image.open(path).convert('RGB');assert im.size==(640,height),im.size
 for y in range(height):
  bits=0
  for c in range(16):bits=bits*2+(sum(im.getpixel((64+17+c*35,y)))<384)
  assert bits==pattern(y//40,y%40),(y,bits,pattern(y//40,y%40))
try:
 wait(lambda:sock.exists());wait(lambda:call('operation.list').get('operations') is not None) if False else time.sleep(1)
 settings=call('settings.get');doc=settings['document'];doc['captureDefaults']={'destination':'local','profileId':None,'publicationMode':'default'};doc['archive']['keepUploads']=True;doc['archive']['root']=str(root/'saved');doc['preferences']['launchAtLogin']=False;doc['preferences']['scrollCaptureFromTop']=False
 for a in doc['actions'].values():
  if 'destination'in a:a.update(destination='default',profileId=None,publicationMode='default')
 call('settings.save',{'document':doc,'expectedRevision':settings['metadata']['acceptedRevision']})
 # The resident resolves output folders at startup.
 resident.terminate();resident.wait();resident=subprocess.Popen([str(build/'putgd'),'--background'],env=env,stdout=log,stderr=log);wait(lambda:sock.exists());time.sleep(1)
 assert call('scroll.capabilities')['available']
 for cap,want in [(30000,'end_of_content'),(2000,'height_cap')]:
  before=set((root/'saved').rglob('*.png'));page();ImageGrab.grab(xdisplay=env['DISPLAY']).save(root/f'fixture-{cap}.png');prepared=call('scroll.prepare',{'rect':[100,60,640,600],'maxHeight':cap});id=prepared['id'];call('scroll.start',{'id':id});ImageGrab.grab(xdisplay=env['DISPLAY']).save(root/f'capturing-{cap}.png')
  result=wait(lambda:(lambda r:r if r['state'] in ('done','failed','cancelled') else None)(call('scroll.inspect',{'id':id})),90)
  assert result['state']=='done',result;assert result['endReason']==want,result
  if want=='height_cap':assert 'Stopped at 2,000 px' in result['note']
  pngs=wait(lambda:list(set((root/'saved').rglob('*.png'))-before));png=pngs[0];verify(png,3200 if cap==30000 else 2000)
  hist=wait(lambda:(lambda h:h if id in json.dumps(h) else None)(call('history.list',{})));assert 'image/png' in json.dumps(hist),hist
  print(want,id,png,flush=True)
 page();id=call('scroll.prepare',{'rect':[100,60,640,600]})['id'];call('scroll.start',{'id':id});call('scroll.cancel',{'id':id});assert call('scroll.inspect',{'id':id})['state']=='cancelled';time.sleep(1)
 assert id not in json.dumps(call('history.list',{}));assert not [p for d in (root/'d').rglob('scroll') for p in d.rglob('*') if p.is_file()]
 assert any('Stopped at 2,000 px' in p.read_text(errors='replace') for p in (root/'s').rglob('*.jsonl'))
 print('PASS history PNG ruler, height cap warning, cancel cleanup',flush=True)
 
finally:
 ImageGrab.grab(xdisplay=env['DISPLAY']).save(root/'final.png')
 if fixture:fixture.terminate();fixture.wait()
 resident.terminate();resident.wait();log.close()
