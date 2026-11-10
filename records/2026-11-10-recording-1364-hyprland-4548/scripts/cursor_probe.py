"""Read-only protocol witness: package helper prepares the same highlighted monitor target.
No recording or timing measurement is performed under protocol tracing.
"""
import importlib.util,pathlib,subprocess,json,time,os
H=pathlib.Path.home();spec=importlib.util.spec_from_file_location('driver',H/'lab/record_run-hide-bar.py');driver=importlib.util.module_from_spec(spec);spec.loader.exec_module(driver)
root=H/'cursor-probe';root.mkdir(mode=0o700,exist_ok=True);env,_=driver.session_environment()
for k,v in [('XDG_CONFIG_HOME','config'),('XDG_DATA_HOME','data'),('XDG_CACHE_HOME','cache'),('XDG_STATE_HOME','state')]:
 p=root/v;p.mkdir(exist_ok=True);env[k]=str(p)
env['WAYLAND_DEBUG']='client';env['PUTGD_RECORD_DEBUG_LOG']=str(root/'helper.debug')
p=subprocess.Popen(['/usr/bin/putgd','--background'],env=env,stdout=open(root/'resident.log','w'),stderr=subprocess.STDOUT)
def cli(method,params={}):
 r=subprocess.run(['/usr/bin/putgd-cli',method,json.dumps(params)],env=env,capture_output=True,text=True);x=json.loads(r.stdout);assert x['ok'],x;return x['result']
try:
 for i in range(120):
  try:cli('recording.capabilities');break
  except Exception:time.sleep(.5)
 settings=cli('settings.get');cli('settings.patch',{'expectedRevision':settings['metadata']['observedRevision'],'patch':{'archive':{'keepUploads':True,'root':str(root/'archive')},'preferences':{'notifications':False}}})
 rid=cli('recording.prepare',{'target':{'kind':'monitor'},'format':'mp4','fps':30,'audio':{'system':False},'clickHighlights':True})['recordingId']
 for i in range(120):
  inspected=cli('recording.inspect',{'id':rid})
  if inspected.get('state')=='ready':break
  time.sleep(.1)
 (root/'inspect.json').write_text(json.dumps(inspected,indent=1));cli('recording.cancel',{'id':rid})
finally:
 cli('ui.quit');p.wait(15)
# Export only cursor protocol lines, plus helper pid/operation identity, not generated profiles.
lines=[]
for source in (root/'state').rglob('*.jsonl'):
 for line in source.read_text().splitlines():
  x=json.loads(line);msg=x.get('message','')
  if any(t in msg for t in ('create_pointer_cursor_session','ext_image_copy_capture_cursor_session_v1','cursor:')) or (msg=='Helper started' and (x.get('fields') or {}).get('operationId')==rid):lines.append(x)
(root/'cursor-witness.json').write_text(json.dumps(dict(recordingId=rid,lines=lines),indent=1));print('cursor witness lines',len(lines))
