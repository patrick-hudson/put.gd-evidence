import os,sys,json,time,subprocess,shutil,hashlib
from pathlib import Path
P=Path('/tmp/v2n');sock=P/'runtime/putgd/session.sock'
cli='/usr/bin/putgd-cli'
def rpc(m,p={}):
 r=subprocess.run([cli,'--socket',str(sock),m,json.dumps(p)],capture_output=True,text=True,timeout=70)
 o=json.loads(r.stdout)
 with (P/'rpc.jsonl').open('a') as f:f.write(json.dumps({'time':time.time(),'method':m,'params':p,'reply':o})+'\n')
 if not o.get('ok'):raise RuntimeError(o)
 return o['result']
def save(n,o):(P/n).write_text(json.dumps(o,indent=2))
def patch(p):
 s=rpc('settings.get');return rpc('settings.patch',{'patch':p,'expectedRevision':s['metadata']['observedRevision']})
if sys.argv[1]=='init':
 assert not P.exists()
 for n in ['config','data','state','cache','runtime','archive','received','cases']:(P/n).mkdir(parents=True,mode=0o700)
 apps=Path.home()/'.local/share/applications';apps.mkdir(parents=True,exist_ok=True);(P/'data/applications').symlink_to(apps,target_is_directory=True)
 env=dict(os.environ);real=env['XDG_RUNTIME_DIR'];env['WAYLAND_DISPLAY']=str(Path(real)/env['WAYLAND_DISPLAY'])
 env.update(PIPEWIRE_RUNTIME_DIR=real,PUTGD_RECORD_DEBUG_LOG=str(P/'helper.log'))
 for k,n in [('XDG_CONFIG_HOME','config'),('XDG_DATA_HOME','data'),('XDG_STATE_HOME','state'),('XDG_CACHE_HOME','cache'),('XDG_RUNTIME_DIR','runtime')]:env[k]=str(P/n)
 assert len(str(sock).encode())<=107
 if os.environ.get('HYPRLAND_INSTANCE_SIGNATURE'):
  paths=[str(P/'runtime/hypr'/os.environ['HYPRLAND_INSTANCE_SIGNATURE']/n) for n in ['.socket.sock','.socket2.sock']];assert all(len(v.encode())<=107 for v in paths);(P/'runtime/hypr').symlink_to(Path(real)/'hypr',target_is_directory=True)
 save('socket-preflight.json',{'path':str(sock),'utf8Bytes':len(str(sock).encode())})
 # Environment stays only in this process; no secret-bearing environment export.
 proc=subprocess.Popen(['/usr/bin/putgd-launcher','--background'],env=env,stdout=(P/'resident.log').open('w'),stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL,start_new_session=True);save('resident.pid',proc.pid)
 for _ in range(200):
  if sock.exists():break
  time.sleep(.1)
 time.sleep(3)
 save('version.json',json.loads(subprocess.check_output([cli,'--version-json'],text=True)))
 save('capabilities.json',rpc('scroll.capabilities'))
 patch({'archive':{'keepUploads':True,'root':str(P/'archive')}})
 # Only this isolated profile's UI process, to prevent its first-run window covering the fixture.
 for d in Path('/proc').iterdir():
  if not d.name.isdecimal():continue
  try:
   if (d/'comm').read_text().strip()=='putgd-ui' and b'XDG_CONFIG_HOME=/tmp/v2n/config\0' in (d/'environ').read_bytes():os.kill(int(d.name),15)
  except (OSError,ProcessLookupError):pass
 receiver=subprocess.Popen(['python3','/home/lab/v2nreceiver.py'],stdout=(P/'receiver.log').open('w'),stderr=subprocess.STDOUT,start_new_session=True);save('receiver.pid',receiver.pid)
 f=P/'loopback.sxcu';f.write_text(json.dumps({'Name':'Synthetic local scroll acceptance','DestinationType':'ImageUploader','RequestMethod':'POST','RequestURL':'http://127.0.0.1:19399/upload','Body':'MultipartFormData','FileFormName':'file','URL':'{json:url}'}))
 s=rpc('settings.get');rpc('settings.importUploader',{'path':str(f),'profileId':'scroll-local','credentialMode':'session','allowInsecureHttp':True,'expectedRevision':s['metadata']['observedRevision']})
 patch({'actions':{'scroll':{'destination':'upload','profileId':'scroll-local'}}})
elif sys.argv[1]=='case':
 name=sys.argv[2];rect=list(map(int,sys.argv[3].split(',')));out=P/'cases'/name;out.mkdir();offset=(P/'helper.log').stat().st_size if (P/'helper.log').exists() else 0
 result={'name':name,'rect':rect};ident=None
 try:
  patch({'preferences':{'scrollCaptureFromTop': 'off' not in name}})
  params={'rect':rect}
  if name.startswith(('gtk','qt')):params['maxHeight']=60000
  if name=='cap':params['maxHeight']=2000
  a=rpc('scroll.prepare',params);ident=a['id'];result['id']=ident
  for _ in range(100):
   if a['state']=='ready':break
   time.sleep(.2);a=rpc('scroll.inspect',{'id':ident})
  rpc('scroll.start',{'id':ident});start=time.monotonic();stopped=False
  while time.monotonic()-start<235:
   a=rpc('scroll.inspect',{'id':ident});(out/'live.json').write_text(json.dumps(a))
   if a['state'] in ['done','failed','cancelled']:break
   if 'stop' in name and not stopped and time.monotonic()-start>.7:rpc('scroll.stop',{'id':ident});stopped=True
   time.sleep(.2)
  result['capture']=a
  if a['state'] not in ['done','failed','cancelled']:rpc('scroll.cancel',{'id':ident})
  sha=a.get('result',{}).get('sha256')
  if sha:
   for _ in range(50):
    found=[f for f in (P/'archive').rglob('*.png') if hashlib.sha256(f.read_bytes()).hexdigest()==sha]
    if found:shutil.copyfile(found[0],out/'capture.png');break
    time.sleep(.3)
  result['history']=rpc('history.list',{'limit':200})
 except Exception as e:result['error']=str(e)
 finally:
  (out/'result.json').write_text(json.dumps(result,indent=2));(out/'helper.log').write_bytes((P/'helper.log').read_bytes()[offset:] if (P/'helper.log').exists() else b'')
 print(json.dumps(result))
elif sys.argv[1]=='patch':print(patch(json.loads(sys.argv[2])))
elif sys.argv[1]=='rpc':print(json.dumps(rpc(sys.argv[2],json.loads(sys.argv[3]) if len(sys.argv)>3 else {})))
