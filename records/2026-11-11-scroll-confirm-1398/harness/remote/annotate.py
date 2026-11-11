import os,subprocess,time,json
from pathlib import Path
P=Path('/tmp/acn2');P.mkdir(mode=0o700);A=Path('/home/patrick/work/scn/squashfs-root');O=Path('/home/patrick/work/scn/pictures');O.mkdir(exist_ok=True)
e=dict(os.environ,HOME=str(P/'home'),QT_QPA_PLATFORM='offscreen',XDG_RUNTIME_DIR=str(P/'r'),XDG_CONFIG_HOME=str(P/'c'),XDG_DATA_HOME=str(P/'d'),XDG_CACHE_HOME=str(P/'cache'),XDG_STATE_HOME=str(P/'s'),LD_LIBRARY_PATH=str(A/'usr/lib')+':'+str(A/'usr/lib/putgd'),QT_PLUGIN_PATH=str(A/'usr/plugins')+':'+str(A/'usr/lib/qt6/plugins'))
for n in ['home','r','c','d','cache','s']:(P/n).mkdir(mode=0o700)
sock=P/'r/putgd/session.sock';assert len(str(sock).encode())<=107
q=subprocess.Popen([str(A/'usr/bin/putgd'),'--background'],env=e,stdout=open(O/'resident.log','w'),stderr=subprocess.STDOUT)
def rpc(m,p={}):
 v=json.loads(subprocess.run([str(A/'usr/bin/putgd-cli'),'--socket',str(sock),m,json.dumps(p)],env=e,text=True,capture_output=True).stdout);
 with open(O/'editor.jsonl','a') as f:f.write(json.dumps({'method':m,'params':p,'reply':v})+'\n')
 return v
try:
 for _ in range(100):
  if sock.exists():break
  time.sleep(.1)
 s=rpc('settings.get')['result'];rpc('settings.patch',{'patch':{'archive':{'keepUploads':True,'root':str(P/'archive')}},'expectedRevision':s['metadata']['observedRevision']})
 specs=[('m74-tray.png','tray.png',None,[[1733,837,174,30]]),('f44-settings.png','settings.png',[530,350,800,140],[[560,382,740,46],[560,432,740,46]]),('m74-capturing.png','capture.png',[75,175,1010,710],[[93,193,974,613],[94,805,460,62]]),('m74-cap.png','height-cap.png',[1400,0,520,115],[[1415,5,490,91]])]
 for source,target,crop,boxes in specs:
  for _ in range(50):
   v=rpc('editor.open',{'source':'file','path':str(O/source)})
   if v['ok']:break
   time.sleep(.2)
  ident=v['result'].get('id') or v['result'].get('operationId');assert ident,v
  commands=[{'op':'add','shape':{'kind':'rectangle','rect':b,'color':'#D7263D','width':4}} for b in boxes]
  if crop:commands.append({'op':'crop','rect':crop})
  for _ in range(100):
   v=rpc('editor.apply',{'id':ident,'commands':commands})
   if v['ok']:break
   time.sleep(.1)
  assert v['ok'],v
  v=rpc('editor.saveCopy',{'id':ident,'path':str(O/target)});assert v['ok'],v
  rpc('editor.cancel',{'id':ident})
finally:
 rpc('ui.quit');q.wait(15)
