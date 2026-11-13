from pathlib import Path
import subprocess,json,os,time,hashlib,argparse,math
from PIL import Image
from item8_campaign import Campaign
p=argparse.ArgumentParser();p.add_argument('--prefix',type=Path,required=True);p.add_argument('--name',required=True);p.add_argument('--sources',type=Path,required=True);a=p.parse_args();r=Path.home()/'work/ocr-final-1428';w=r/a.name;w.mkdir(mode=0o700);rt=Path('/tmp')/('iq'+hashlib.sha256(a.name.encode()).hexdigest()[:7]);rt.mkdir(mode=0o700);runtime=rt/'r';runtime.mkdir(mode=0o700);sock=runtime/'putgd/session.sock';assert len(str(sock).encode())<=107;env=dict(HOME=str(Path.home()),USER='patrick',LOGNAME='patrick',PATH='/usr/bin:/bin',LANG='C.UTF-8',QT_QPA_PLATFORM='offscreen',XDG_RUNTIME_DIR=str(runtime),XDG_CONFIG_HOME=str(w/'c'),XDG_DATA_HOME=str(w/'d'),XDG_STATE_HOME=str(w/'s'),XDG_CACHE_HOME=str(w/'k'));(w/'private-env.json').write_text(json.dumps(env));(w/'session-env.json').write_text(json.dumps(env));build=json.loads(subprocess.check_output([str(a.prefix/'bin/putgd-cli'),'--version-json'],text=True));(w/'state.json').write_text(json.dumps({'nativePrefix':str(a.prefix),'socket':str(sock),'build':build,'socketBytes':len(str(sock).encode())}));app=subprocess.Popen([str(a.prefix/'bin/putgd'),'--background','-platform','offscreen'],env=env,stdout=(w/'app.log').open('x'),stderr=subprocess.STDOUT);rows=[];exports=w/'exports';exports.mkdir(mode=0o700)
def overlap(x,y):return x[0]<y[2] and x[2]>y[0] and x[1]<y[3] and x[3]>y[1]
try:
 end=time.monotonic()+20
 while not sock.exists() and time.monotonic()<end:time.sleep(.05)
 c=Campaign(w);c.patch({'actions':{'edit':{'destination':'local','profileId':None}},'archive':{'root':str(w/'archive'),'keepUploads':True}})
 def open_ready(path):
  end=time.monotonic()+10
  while True:
   try:return c.open_editor(path)
   except RuntimeError as e:
    if str(e)!='editor_active' or time.monotonic()>=end:raise
    time.sleep(.1)
 for path in sorted(a.sources.glob('*.png')):
  gt=json.loads(path.with_suffix('.truth.json').read_text())['words'];positive=[g for g in gt if g['category'] not in ['control','clean']];negative=[g for g in gt if g['category'] in ['control','clean']];row={'page':path.name,'sourceSha256':hashlib.sha256(path.read_bytes()).hexdigest(),'status':'not_run'};op=None
  try:
   op,state=open_ready(path);result=c.call('editor.apply',{'id':op,'commands':[{'op':'redactText','categories':['email','phone','ip','card','key']}]});state=c.call('editor.inspect',{'id':op});rects=[[s['rect'][0],s['rect'][1],s['rect'][0]+s['rect'][2],s['rect'][1]+s['rect'][3]] for s in state['shapes'] if s['kind']=='redact'];out=exports/path.name;c.call('editor.saveCopy',{'id':op,'path':str(out)});im=Image.open(out).convert('RGBA');black=lambda box:im.crop((math.floor(box[0]),math.floor(box[1]),math.ceil(box[2]),math.ceil(box[3]))).getextrema()==((0,0),(0,0),(0,0),(255,255));covered=[black(g['box']) for g in positive];row.update(status='measured',targetItems=len(positive),coveredItems=sum(covered),uncoveredItems=[i for i,v in enumerate(covered) if not v],redactMarks=len(rects),extraMarks=sum(not any(overlap(x,g['box']) for g in positive) or any(overlap(x,g['box']) for g in negative) for x in rects),rects=rects,allMarksOpaqueBlack=all(black(x) for x in rects),exportSha256=hashlib.sha256(out.read_bytes()).hexdigest(),counts=result.get('counts'))
  except Exception as e:row['reason']=str(e) if isinstance(e,RuntimeError) else type(e).__name__
  finally:
   if op:c.raw('editor.cancel',{'id':op})
  rows.append(row);(w/'receipt.json').write_text(json.dumps({'build':build,'scope':'Real editor/helper offscreen and exported pixels; no desktop pipeline claim. Existing fixed source images, unmodified.','rows':rows},indent=2));print(path.name,row['status'],row.get('coveredItems'),row.get('targetItems'),row.get('extraMarks'),flush=True)
finally:app.terminate();app.wait(timeout=10);(w/'closed.json').write_text(json.dumps({'closed':True}))
