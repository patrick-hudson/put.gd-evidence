import subprocess,os,pathlib,json,time,sys,signal,hashlib
root=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(root/'lab'));import record_run
runs=root/'r';runs.mkdir(mode=0o700,exist_ok=True)
env,_=record_run.session_environment();app=next(root.glob('*.AppImage'));an=root/'an/squashfs-root'
meta={'startedUtc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'loadAtStart':os.getloadavg(),'appimageSha256':hashlib.sha256(app.read_bytes()).hexdigest(),'order':[],'systemSink':None}
state=root/'shared-audio.json';tone=None
base=['python3',str(root/'runner.py'),'--build','pr='+str(app),'--analyzer',str(an),'--video','marker','--rounds','1','--no-notifications','--keep-unpaired','--vnc-port','0','--click-vnc','10.0.2.2:5946','--video-size','640x360','--frames','--format','mp4','--mic','off','--system','tone','--pause-for','0','--pause-at','14','--after','2','--click','4,200,100,left','--click','8,640,100,right','--click','12,1100,100,middle']
def save(): (root/'matrix.json').write_text(json.dumps(meta,indent=2)+'\n')
def one(tag,target,on,lead,rep,extra=[]):
 d=runs/tag;d.mkdir(mode=0o700)
 subprocess.run(['python3',str(root/'check_socket_paths.py'),'--socket','/run/user/1000/putgd/session.sock'],check=True)
 os.link(root/'marker.mkv',d/'marker.mkv')
 argv=base+['--run',str(d),'--target',target,'--click-highlights',on,'--lead',str(lead)]+(['--rect','0,0,1280,400']if target=='region'else[])+extra
 row={'tag':tag,'target':target,'highlights':on,'lead':lead,'repeat':rep,'startedUtc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'loadAtStart':os.getloadavg(),'command':argv}
 with open(runs/(tag+'.log'),'w')as f:
  f.write(json.dumps(row)+'\n');f.flush();p=subprocess.run(argv,stdout=f,stderr=subprocess.STDOUT,env=dict(os.environ,PUTGD_RECORD_DEBUG_LOG=str(runs/(tag+'.debug'))))
 row.update(exitCode=p.returncode,loadAtEnd=os.getloadavg())
 try:
  x=json.loads((d/'results.json').read_text());e=x['rounds'][0];c=e.get('clips',{}).get('export',{})
  row.update(medianMs=c.get('medianMs'),pairs=c.get('pairs'),offsetsMs=c.get('offsetsMs'),pairTimesS=c.get('pairTimesS'),motion=c.get('motion'),frame=e.get('frame'),error=e.get('error')or x.get('error'),problems=e.get('problems'),clicks=c.get('clickCheck'),delayedCaptures=e.get('delayedCaptures'))
 except Exception as error:row['readError']=str(error)
 meta['order'].append(row);save()
 print(json.dumps({k:row.get(k)for k in('tag','medianMs','pairs','motion','error','exitCode','loadAtStart','loadAtEnd')}),flush=True)
try:
 p=subprocess.run(['python3',str(root/'lab/virtual_mic.py'),'create','--name','putgd_lab_matrix_'+str(os.getpid()),'--state',str(state),'--system-sink','--no-microphone'],env=env,capture_output=True,text=True,check=True)
 meta['audioCreated']=json.loads(p.stdout);meta['systemSink']=json.loads(state.read_text())['systemSink'];save()
 tone=subprocess.Popen(['python3',str(root/'lab/virtual_mic.py'),'tone','--state',str(state),'--seconds','7200'],env=env,stdout=open(root/'tone.log','w'),stderr=subprocess.STDOUT,start_new_session=True)
 subprocess.run([str(an/'usr/bin/putgd-record'),'--av-marker',str(root/'marker.mkv'),'60','--moving'],check=True,env=dict(os.environ,APPDIR=str(an)),stdout=open(root/'marker-generation.log','w'),stderr=subprocess.STDOUT)
 meta['markerSha256']=hashlib.sha256((root/'marker.mkv').read_bytes()).hexdigest();save()
 for target in ('region','monitor'):
  meta[target+'LoadAtStart']=os.getloadavg();save()
  for rep in range(1,5):
   for lead in ((3,6)if rep%2 else(6,3)):
    for on in ('on','off'):one(f'{target}-{rep}-{on}-{lead}',target,on,lead,rep)
  meta[target+'LoadAtEnd']=os.getloadavg();save()
  if target=='region':one('g-retained','monitor','on',3,0,['--delayed-capture','desktop:3'])
finally:
 if tone and tone.poll()is None:
  os.killpg(tone.pid,signal.SIGTERM);tone.wait(15)
 if state.exists():
  p=subprocess.run(['python3',str(root/'lab/virtual_mic.py'),'remove','--state',str(state)],env=env,capture_output=True,text=True)
  meta['audioRemoved']={'exitCode':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
 meta['loadAtEnd']=os.getloadavg();meta['finishedUtc']=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime());save()
