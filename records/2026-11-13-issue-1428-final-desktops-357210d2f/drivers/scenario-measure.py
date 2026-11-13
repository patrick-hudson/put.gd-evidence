import json,os,subprocess,time,sys,hashlib
from pathlib import Path

def extra(r):
 base=Path(__file__).parent;out=r.receipt['measurements']={'loadBefore':list(os.getloadavg()),'cpus':os.cpu_count(),'sourceSha256':hashlib.sha256((base/'dense.png').read_bytes()).hexdigest(),'ackObservation':'Monotonic client receipt after text.inspect copied acknowledgement; polling <=30ms plus CLI roundtrip. Server phase durations are retained independently.'}
 def cpu_sample():
  def read():return list(map(int,Path('/proc/stat').read_text().splitlines()[0].split()[1:9]))
  a=read();time.sleep(1);b=read();d=[y-x for x,y in zip(a,b)];return {'seconds':1,'busyPercent':round(100*(sum(d)-d[3]-d[4])/sum(d),2),'load':list(os.getloadavg())}
 out['cpuSampleBefore']=cpu_sample()
 pid=r.resident_pid()
 out['residentIdentity']={'pid':pid,'executable':os.readlink('/proc/'+str(pid)+'/exe'),'runtime':r.private['XDG_RUNTIME_DIR']}
 entries=[]
 for folder in [Path('/usr/share/applications'),Path.home()/'.local/share/applications',Path(r.private['XDG_DATA_HOME'])/'applications']:
  if not folder.exists():continue
  for f in folder.glob('*putgd*.desktop'):
   rows=[x for x in f.read_text(errors='replace').splitlines() if x.startswith(('Exec=','X-KDE-DBUS-Restricted-Interfaces=','X-PutGD-AppImage-Owner='))]
   if any(out['residentIdentity']['executable'] in x for x in rows if x.startswith('Exec=')):entries.append({'path':str(f),'fields':rows})
 out['matchingPermissionEntries']=entries
 out['uiChildPolicy']='Leave the owned UI behind the visibly confirmed fullscreen fixture; quit normally with the resident during cleanup.'
 def watch(name):
  events=r.root/(name+'-events.jsonl');p=subprocess.Popen(['sudo','-n','python3','-I',str(base/'lifecycle_watch.py'),str(events),'putgd-ocr',str(pid)])
  r.wait(events.exists,name+' observer ready');return p,events
 def stop(p):
  if p.poll() is None:subprocess.run(['sudo','-n','kill',str(p.pid)]);p.wait(timeout=10)
 latency_watch,events=watch('latency')
 try:
  for mode,rect in [('dense',[459,44,1462,1036]),('paragraph',[550,430,1370,650])]:
   if os.environ.get('PUTGD_POST_TEXT_ONLY')=='1' or mode not in os.environ.get('PUTGD_LATENCY_MODES','dense paragraph').split():continue
   (base/'mode').write_text(mode);time.sleep(1);r.input.click(960,540);time.sleep(.4)
   port=os.environ.get('PUTGD_MEASUREMENT_VNC_PORT')
   if port:
    try:
     sys.path.insert(0,str(base));from rfb import RFB
     v=RFB(int(port));v.frame();v.frame();v.screenshot(str(r.root/('measurement-'+mode+'.png')));v.close()
    except Exception as e:out.setdefault('frameErrors',[]).append({'mode':mode,'error':str(e)})
   rows=[];out[mode]=rows
   for n in range(5):
    sentinel='measurement-sentinel-'+mode+'-'+str(n);r.copy_sentinel(sentinel);assert r.paste()==sentinel
    op=r.cli('text.recognize',{'source':'region','copy':True})['result']['operationId'];r.wait(lambda:r.cli('text.inspect',{'id':op})['result']['state']=='acquiring','latency selector');time.sleep(1.5)
    if os.environ.get('PUTGD_SELECTOR_FRAMES')=='1':
     try:
      vnc=RFB(int(port));vnc.frame();vnc.frame();vnc.screenshot(str(r.root/(mode+'-selector-'+str(n)+'.png')));vnc.close()
     except Exception as e:out.setdefault('frameErrors',[]).append({'selector':n,'error':str(e)})
    r.input.drag(rect[:2],rect[2:]);end=time.monotonic_ns();deadline=time.monotonic()+40
    while True:
     v=r.cli('text.inspect',{'id':op})['result']
     if v['state'] in ('completed','failed','cancelled'):break
     if time.monotonic()>deadline:
      out['acquisitionFailure']={'operationId':op,'lastInspect':v,'paste':r.paste(),'sentinel':sentinel}
      out['acquisitionFailure']['cancel']=r.cli('text.cancel',{'id':op},check=False)
      raise RuntimeError('Latency job timeout')
     time.sleep(.03)
    ack=time.monotonic_ns();paste=r.paste();t=v.get('timings',{})
    row={'operationId':op,'selection':rect,'pixels':(rect[2]-rect[0])*(rect[3]-rect[1]),'state':v['state'],'copyStatus':v.get('copyStatus'),'timings':t,'selectionToObservedAckMs':(ack-end)/1e6,'clipboardMatchesResult':paste==v.get('text'),'characters':v.get('characterCount'),'truncated':v.get('truncated'),'banded':v.get('banded'),'helperAbsentAfter':not subprocess.run(['pgrep','-x','putgd-ocr'],capture_output=True,text=True).stdout.strip()}
    row['measured']=v['state']=='completed' and v.get('copyStatus')=='copied' and bool(paste) and row['clipboardMatchesResult'] and all(type(t.get(k))==int and t[k]>=0 for k in ('spawnMs','engineStartMs','recognizeMs','copyMs','totalMs'))
    rows.append(row);print(json.dumps({'measurement':mode,'row':row}),flush=True)
 finally:
  stop(latency_watch);out['latencyHelperEvents']=[json.loads(x) for x in events.read_text().splitlines() if x.strip()]
 out['cpuSampleAfterLatency']=cpu_sample()
 if os.environ.get('PUTGD_LATENCY_ONLY')=='1':
  out['postText']={'status':'not_repeated','reason':'Quiet latency repeat only; exact candidate 25-job/180s workload is retained in the earlier measurement receipt.'};return
 r.input.stream.close();r.input.socket.close()
 watch_proc,events=watch('workload')
 try:
  (base/'mode').write_text('paragraph');time.sleep(1)
  try:
   sys.path.insert(0,str(base));from rfb import RFB
   vnc=RFB(int(os.environ['PUTGD_MEASUREMENT_VNC_PORT']));vnc.frame();vnc.frame();vnc.screenshot(str(r.root/'post-text-fixture.png'));vnc.close()
  except Exception as e:out.setdefault('frameErrors',[]).append({'postText':str(e)})
  driver=r.root/'region_input.py';driver.write_text('#!/usr/bin/python3\nimport sys,time\nsys.path.insert(0,'+repr(str(base))+')\nfrom text_proof import Input\ni=Input('+repr(r.input_path)+',1920,1080)\ntime.sleep(.8)\ni.drag((550,430),(1370,650))\n');driver.chmod(0o700)
  sys.path.insert(0,os.environ['PUTGD_MEASUREMENT_SOURCE']+'/tests/performance/text')
  from workload import run
  from types import SimpleNamespace
  receipt={'schemaVersion':1,'status':'blocked','jobs':[]}
  try:run(SimpleNamespace(pid=r.resident_pid(),socket=Path(r.socket),cli=r.args.cli,region_driver=str(driver),helper_events=events),receipt)
  except Exception as e:receipt['reason']=str(e)
  (r.root/'workload.json').write_text(json.dumps(receipt,indent=2));out['postText']=receipt
  if receipt.get('status')=='measured':
   from tools.lab.surface_driver.recipes.outcomes import judge_idle
   try:judge_idle(receipt['memory']);out['gateC']={'status':'passed','evaluator':'candidate frozen judge_idle'}
   except Exception as e:out['gateC']={'status':'blocked' if type(e).__name__=='RecipeBlocked' else 'failed','reason':str(e),'evaluator':'candidate frozen judge_idle'}
 finally:stop(watch_proc)
 out['loadAfter']=list(os.getloadavg())
 print('MEASUREMENTS '+json.dumps({'postTextStatus':out['postText']['status'],'reason':out['postText'].get('reason'),'memory':out['postText'].get('memory')}),flush=True)
