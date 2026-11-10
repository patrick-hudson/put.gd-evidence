import os,sys,json,subprocess,time,pathlib,threading
root=pathlib.Path('/tmp/c1364'); env=os.environ.copy();env['XDG_RUNTIME_DIR']='/run/user/1000'
def cmd(args): return subprocess.check_output(args,env=env,text=True).strip()
def audio(): return {k:cmd(['pactl','get-default-'+k]) for k in ('sink','source')}
original=audio(); (root/'original-audio.json').write_text(json.dumps(original))
def observe(stop):
 while not stop.wait(.2):
  for p in pathlib.Path('/proc').iterdir():
   try:
    if p.name.isdigit() and (p/'comm').read_text().strip()=='putgd':
     lines=[l for l in (p/'maps').read_text().splitlines() if 'libQt6Core' in l]
     if lines: (root/'loaded-qt.txt').write_text('\n'.join(lines)); return
   except (OSError,ProcessLookupError): pass
stop=threading.Event(); threading.Thread(target=observe,args=(stop,),daemon=True).start()
base=['python3',str(root/'lab/record_run.py'),'--build','pr='+str(root/'pkg/usr/bin'),'--analyzer',str(root/'pkg'),'--video','marker','--rounds','1','--no-notifications','--keep-unpaired','--frames']
reg=['--target','region','--rect','0,0,960,540']
click=['--format','mp4','--lead','3','--system','tone','--pause-for','0','--pause-at','14','--after','2','--click','4,300,100,left','--click','8,700,100,right','--click','12,1100,100,middle']
cases=[('a',reg+['--format','mp4','webm','--mic','virtual','--system','off','--lead','6','--pause-for','0','--pause-at','12','--after','2']),('b',reg+['--format','mp4','webm','--mic','virtual','--system','tone','--lead','6','--pause-at','8','--pause-for','3','--after','8']),('c',reg+['--format','mp4','--mic','muted','--system','tone','--lead','6','--pause-for','0','--pause-at','10','--after','2']),('d',reg+['--format','mp4','--mic','virtual','--system','leak','--unplug-at','6','--lead','6','--pause-for','0','--pause-at','12','--after','2']),('e',reg+['--format','mp4','--mic','default','--system','off','--lead','6','--pause-for','0','--pause-at','4','--after','1']),('f',reg+['--format','mp4','--mic','late','--system','off','--lead','3','--pause-for','0','--pause-at','8','--after','2','--min-pairs','5']),('g-fallback',reg+['--format','mp4','--mic','off','--system','tone','--lead','3','--pause-for','0','--pause-at','12','--after','2','--output-gone-at','6','--output-fallback']),('g-none',reg+['--format','mp4','--mic','off','--system','tone','--lead','3','--pause-for','0','--pause-at','12','--after','2','--output-gone-at','6','--cards-off'])]
for target in ('monitor','region','window'):
 for setting in ('on','off'):
  cases.append(('h-'+target+'-'+setting,['--target',target]+(['--rect','0,0,1280,400'] if target=='region' else [])+click+['--click-highlights',setting]))
cases.append(('i',['--target','monitor']+click+['--delayed-capture','desktop:3']))
for name,args in cases:
 if len(sys.argv)>1 and name not in sys.argv[1:]: continue
 path=root/name
 if path.exists(): raise RuntimeError('existing run '+name)
 # Harness uses the session runtime path, no run-directory prefix.
 socket='/run/user/1000/putgd/session.sock'; assert len(socket.encode())<=107
 (root/(name+'-socket.json')).write_text(json.dumps({'path':socket,'utf8Bytes':len(socket.encode()),'passed':True}))
 module=None
 try:
  if name!='g-none':
   module=cmd(['pactl','load-module','module-null-sink','sink_name=putgd_lab_outer','sink_properties=device.description=PrivateAcceptance'])
   subprocess.check_call(['pactl','set-default-sink','putgd_lab_outer'],env=env)
  print('START',name,cmd(['uptime']),flush=True)
  with (root/(name+'.log')).open('w') as log:
   rc=subprocess.call(base+['--run',str(path)]+args,env=env,stdout=log,stderr=subprocess.STDOUT)
  print('END',name,'rc',rc,flush=True)
  if (path/'results.json').exists(): subprocess.run(['python3',str(root/'lab/summarize_run.py'),str(path/'results.json')])
 finally:
  for kind,value in original.items(): subprocess.run(['pactl','set-default-'+kind,value],env=env,check=True)
  if module: subprocess.run(['pactl','unload-module',module],env=env,check=True)
  state={'defaults':audio(),'modules':cmd(['pactl','list','short','modules']),'sources':cmd(['pactl','list','short','sources'])}
  (root/(name+'-audio-after.json')).write_text(json.dumps(state,indent=2))
  assert state['defaults']==original
  assert 'putgd_lab' not in state['modules']
stop.set()
