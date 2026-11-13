from pathlib import Path
import subprocess,json,os,time,socket,struct,signal,hashlib
from workload import call,validate_socket
r=Path.home()/'work/ocr-corpus-1428';root=Path.home()/'work/i8dense';root.mkdir(mode=0o700);desktop=json.loads((Path.home()/'work/i8m/desktop-env.json').read_text());source=r/'candidate-corpus/m74-captures/m74-terminal-dense-light-100.png';viewer=subprocess.Popen(['feh','--fullscreen','--zoom','100','--title','putgd-item8-dense-repeat',str(source)],env=desktop,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(.5);viewwin=subprocess.check_output(['xdotool','search','--pid',str(viewer.pid)],env=desktop,text=True).splitlines()[-1];cli=r/'ubuntu24-candidate/usr/bin/putgd-cli'
try:
 for index,kind in enumerate(['native']):
  w=root/kind;w.mkdir(mode=0o700);rt=Path('/tmp/i8dr'+str(index)+'1428');rt.mkdir(mode=0o700);runtime=rt/'r';runtime.mkdir(mode=0o700);sock=runtime/'putgd/session.sock';assert len(str(sock).encode())<=107;env=desktop|dict(XDG_RUNTIME_DIR=str(runtime),XDG_CONFIG_HOME=str(w/'c'),XDG_DATA_HOME=str(w/'d'),XDG_STATE_HOME=str(w/'s'),XDG_CACHE_HOME=str(w/'k'));binary=r/'ubuntu24-candidate/usr/bin/putgd' if kind=='native' else r/'putgd-26.1113.4836-dev+gfe838a950216-x86_64.AppImage';app=subprocess.Popen([str(binary),'--background'],env=env,stdout=(w/'app.log').open('x'),stderr=subprocess.STDOUT);pid=None
  try:
   end=time.monotonic()+20
   while not sock.exists() and time.monotonic()<end:time.sleep(.05)
   with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as peer:peer.connect(str(sock));pid,uid,_=struct.unpack('3i',peer.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12))
   assert uid==os.getuid();validate_socket(sock,pid);time.sleep(.5);ownedUi=[]
   for task in Path('/proc',str(pid),'task').glob('*/children'):
    for child in map(int,task.read_text().split()):
     if Path('/proc',str(child),'comm').read_text().strip()=='putgd-ui':ownedUi.append(child);os.kill(child,signal.SIGTERM)
   subprocess.run(['xdotool','windowactivate','--sync',viewwin],env=desktop,check=True);time.sleep(.5);subprocess.run(['import','-window',viewwin,str(w/'owned-viewer-after-start.png')],env=desktop,check=True);state={'kind':kind,'pid':pid,'exe':os.readlink('/proc/'+str(pid)+'/exe'),'socket':str(sock),'cli':str(cli),'socketBytes':len(str(sock).encode()),'closedOwnedUiPids':ownedUi,'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'selection':[460,45,1001,990],'loadBefore':os.getloadavg(),'cpus':os.cpu_count()};(w/'identity.json').write_text(json.dumps(state,indent=2));driver=Path.home()/'work/i8m/native/select.py';drivertext=driver.read_text().replace("w=Path(__file__).parent;s=", "w=Path("+repr(str(w))+");s=");(w/'state.json').write_text(json.dumps(state));(w/'select.py').write_text(drivertext);(w/'select.py').chmod(0o700);rows=[]
   for n in range(30):
    op=call(str(cli),sock,'text.recognize',{'source':'region','copy':True})['operationId'];subprocess.run([str(w/'select.py'),op],env=env,check=True,timeout=20);end=json.loads((w/'selection-times.jsonl').read_text().splitlines()[-1])['selectionEndNs'];deadline=time.monotonic()+30
    while time.monotonic()<deadline:
     v=call(str(cli),sock,'text.inspect',{'id':op})
     if v['state'] in ['completed','failed','cancelled']:break
     time.sleep(.03)
    ack=time.monotonic_ns();paste=subprocess.run(['xclip','-selection','clipboard','-o'],env=desktop,capture_output=True,timeout=10);t=v.get('timings',{});measured=v['state']=='completed' and v.get('copyStatus')=='copied' and len(v.get('text',''))>7000 and not v.get('codes') and paste.returncode==0 and paste.stdout==v['text'].encode() and all(type(t.get(k))==int and t[k]>=0 for k in ['spawnMs','engineStartMs','recognizeMs','copyMs','totalMs']);rows.append({'operationId':op,'status':'measured' if measured else 'blocked','state':v['state'],'copyStatus':v.get('copyStatus'),'timings':t,'characterCount':v.get('characterCount'),'selectionToObservedAckMs':(ack-end)/1e6,'independentPasteMatches':paste.stdout==v.get('text','').encode(),'textSha256':hashlib.sha256(v.get('text','').encode()).hexdigest()});(w/'receipt.json').write_text(json.dumps({'complete':len(rows)==30 and all(x['status']=='measured' for x in rows),'rows':rows},indent=2))
   print('DENSE30',kind,'p95',sorted(x['selectionToObservedAckMs'] for x in rows)[28],'chars',rows[-1]['characterCount'],flush=True)
  except Exception as e:(w/'blocked.json').write_text(json.dumps({'reason':str(e)}));print('BLOCKED',kind,type(e).__name__,str(e),flush=True)
  finally:
   if pid and Path('/proc',str(pid)).exists():os.kill(pid,signal.SIGTERM)
   if app.poll() is None:app.wait(timeout=10)
finally:
 viewer.terminate();viewer.wait(timeout=5);(root/'closed.json').write_text(json.dumps({'closed':True}))
