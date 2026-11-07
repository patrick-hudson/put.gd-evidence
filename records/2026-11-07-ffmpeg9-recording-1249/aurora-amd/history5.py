import sys,os,time,json,argparse,subprocess,shutil
from pathlib import Path
root=Path.home()/'work/f9t';sys.path.insert(0,str(root/'tools/lab'));import record_run as r
args=argparse.Namespace(run=str(root/(sys.argv[3] if len(sys.argv)>3 else 'history3')),real_data_home=sys.argv[1]=='yes',analyzer=str(root/'analyzer/squashfs-root'),video='still',output=None,video_size=None,audio_device=None,vnc_port=5900)
d=r.Driver(args);out={};pat=sys.argv[2]
try:
 for label in ['candidate','nightly']:
  b=r.Build(label,str(next((Path.home()/'work/ff9-rec-1249'/label).glob('*.AppImage'))),d.run)
  d.start_resident(b);d.stop_resident(b)
 d.open_cover()
 for label in ['candidate','nightly']:
  b=r.Build(label,str(next((Path.home()/'work/ff9-rec-1249'/label).glob('*.AppImage'))),d.run)
  try:
   d.start_resident(b)
   for attempt in range(40):
    try:
     prepared=d.cli(b,'recording.prepare',{'target':{'kind':'monitor'},'format':'mp4','fps':30,'audio':{'system':False}});break
    except r.RunError as error:
     if 'initializing' not in str(error):raise
     time.sleep(.5)
   rid=prepared['recordingId'];d.wait_state(b,rid,('ready',),120)
   d.cli(b,'recording.start',{'id':rid});d.cli(b,'recording.overlay',{'id':rid,'visible':False});time.sleep(2)
   stopped=d.cli(b,'recording.stop',{'id':rid})
   accepted=d.cli(b,'recording.upload',{'id':rid,'revision':stopped['edit']['revision']})
   out[label]={'accepted':accepted}
   oid=accepted.get('operationId') or accepted.get('id')
   for _ in range(120):
    op=d.cli(b,'operation.inspect',{'id':oid})
    if op.get('state') in ['completed','failed','cancelled']:break
    time.sleep(.25)
   out[label]['operation']=op
   hs=d.cli(b,'history.list',{'limit':10});out[label]['history']=hs
   items=hs.get('records',[])
   hid=items[0]['id']
   prev=d.cli(b,'history.preview',{'id':hid});out[label]['preview']=prev
   if prev.get('previewPath'):shutil.copyfile(prev['previewPath'],d.run/'frames'/f'{label}-history-poster.png')
   d.cli(b,'ui.show',{'view':'history'})
   out[label]['ui']=d.cli(b,'ui.history',{'action':'select','ids':[hid]})
   time.sleep(2)
   out[label]['details']=d.cli(b,'ui.history',{'action':'openDetails'})
   time.sleep(1)
   from rfb import RFB
   v=RFB(args.vnc_port);frame=d.run/'frames'/f'{label}-history.png';v.screenshot(str(frame));v.close()
   checked=subprocess.run(['python3',str(root/'tools/lab/cover_player.py'),'check-frame',str(frame)],capture_output=True,text=True)
   out[label]['frame']=json.loads(checked.stdout)
  except Exception as e:out.setdefault(label,{})['error']=str(e)
  finally:d.stop_resident(b)
finally:
 d.close_cover()
 if d.real_data is not None and d.real_data.exists():d.real_data.rename(d.run/'real-data-putgd')
 (d.run/'results.json').write_text(json.dumps(out,indent=1)+'\n')
print(json.dumps(out))
