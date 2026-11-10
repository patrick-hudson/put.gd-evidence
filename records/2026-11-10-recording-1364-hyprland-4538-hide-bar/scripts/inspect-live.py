import pathlib,sys,os,subprocess,json
H=pathlib.Path.home();sys.path.insert(0,str(H/'lab'));import record_run
run=H/'f/monitor-on';ids=list((run/'data/putgd/recording').glob('*/working.mkv'));assert len(ids)==1
rid=ids[0].parent.name;env,_=record_run.session_environment()
for k,v in [('XDG_CONFIG_HOME','config'),('XDG_DATA_HOME','data'),('XDG_STATE_HOME','state'),('XDG_CACHE_HOME','cache')]:env[k]=str(run/v)
r=subprocess.run(['/usr/bin/putgd-cli','recording.inspect',json.dumps({'id':rid})],env=env,capture_output=True,text=True);x=json.loads(r.stdout);assert x['ok'];(H/'inspect-monitor.json').write_text(json.dumps(x,indent=1));print(x['result']['state'],x['result']['overlayExcluded'],x['result']['overlayPlacement'])
