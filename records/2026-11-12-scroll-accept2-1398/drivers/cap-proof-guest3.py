from pathlib import Path
import os,json,time,subprocess,hashlib,shutil,sys,struct
P=Path('/tmp/cp3');P.mkdir(mode=0o700)
for n in ['c','d','s','cache','runtime','archive','case']:(P/n).mkdir(mode=0o700)
apps=Path.home()/'.local/share/applications';apps.mkdir(parents=True,exist_ok=True);(P/'d/applications').symlink_to(apps,target_is_directory=True)
e=dict(os.environ);real=e['XDG_RUNTIME_DIR'];e['WAYLAND_DISPLAY']=str(Path(real)/e['WAYLAND_DISPLAY']);e['PIPEWIRE_RUNTIME_DIR']=real;e['PUTGD_RECORD_DEBUG_LOG']=str(P/'helper.log')
paths=[P/'runtime/putgd/session.sock'];sig=e.get('HYPRLAND_INSTANCE_SIGNATURE')
if sig:
 for name in ['.socket.sock','.socket2.sock']:paths += [P/'runtime/hypr'/sig/name,Path(real)/'hypr'/sig/name]
 (P/'runtime/hypr').symlink_to(Path(real)/'hypr',target_is_directory=True)
assert all(len(str(x).encode())<=107 and len(str(x.resolve()).encode())<=107 for x in paths)
(P/'socket-preflight.json').write_text(json.dumps({str(x):{'rawUtf8':len(str(x).encode()),'resolvedUtf8':len(str(x.resolve()).encode())} for x in paths},indent=2))
for k,n in [('CONFIG','c'),('DATA','d'),('STATE','s'),('CACHE','cache'),('RUNTIME','runtime')]:e['XDG_'+k+('_DIR' if k=='RUNTIME' else '_HOME')]=str(P/n)
cli=str(Path.home()/'putgd-lab/bin/putgd-cli');launcher=str(Path.home()/'putgd-lab/bin/putgd-launcher');q=subprocess.Popen([launcher,'--background'],env=e,stdout=open(P/'resident.log','w'),stderr=subprocess.STDOUT,start_new_session=True);(P/'resident.pid').write_text(str(q.pid))
for _ in range(200):
 if paths[0].exists():break
 time.sleep(.1)
def rpc(m,a={}):
 x=subprocess.run([cli,'--socket',str(paths[0]),m,json.dumps(a)],env=e,capture_output=True,text=True,timeout=75);v=json.loads(x.stdout)
 with open(P/'rpc.jsonl','a') as f:f.write(json.dumps({'time':time.time(),'method':m,'params':a,'reply':v})+'\n')
 assert v['ok'],v
 return v['result']
s=rpc('settings.get');doc=s['document'];doc['preferences']['notifications']=False;doc['preferences']['scrollCaptureFromTop']=True;doc['archive'].update(keepUploads=True,root=str(P/'archive'));rpc('settings.save',{'document':doc,'expectedRevision':s['metadata']['observedRevision']});time.sleep(3)
for x in Path('/proc').iterdir():
 if not x.name.isdigit():continue
 try:
  if (x/'comm').read_text().strip()=='putgd-ui' and ('XDG_CONFIG_HOME='+str(P/'c')).encode() in (x/'environ').read_bytes().split(bytes([0])):os.kill(int(x.name),15)
 except OSError:pass
time.sleep(2);sx=P/'loopback.sxcu';sx.write_text(json.dumps({'Name':'Synthetic cap receiver proof','DestinationType':'ImageUploader','RequestMethod':'POST','RequestURL':'http://127.0.0.1:19511/upload','Body':'MultipartFormData','FileFormName':'file','URL':'{json:url}'}));s=rpc('settings.get');rpc('settings.importUploader',{'path':str(sx),'profileId':'cap-local','credentialMode':'session','allowInsecureHttp':True,'expectedRevision':s['metadata']['observedRevision']});s=rpc('settings.get');rpc('settings.patch',{'patch':{'preferences':{'notifications':True},'actions':{'scroll':{'destination':'upload','profileId':'cap-local'}}},'expectedRevision':s['metadata']['observedRevision']});(P/'version.json').write_text(subprocess.check_output([cli,'--version-json'],text=True));(P/'capabilities.json').write_text(json.dumps(rpc('scroll.capabilities'),indent=2))
server=subprocess.Popen(['python3','/home/lab/cap-receiver3.py'],stdout=open(P/'receiver.log','w'),stderr=subprocess.STDOUT,start_new_session=True);(P/'hold-upload').touch();fixture=subprocess.Popen(['python3','/home/lab/cap-ruler.py','--rows','600'],env=dict(e,SC_Y='100'),stdout=open(P/'fixture.log','w'),stderr=subprocess.STDOUT,start_new_session=True);time.sleep(5)
v=rpc('scroll.prepare',{'rect':[100,100,960,600],'maxHeight':2000});ident=v['id']
while v['state']!='ready':time.sleep(.1);v=rpc('scroll.inspect',{'id':ident})
(P/'ready').write_text('ready')
for _ in range(300):
 if (P/'start-verified').exists():break
 time.sleep(.1)
else:raise RuntimeError('independent ready viewport not verified')
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
