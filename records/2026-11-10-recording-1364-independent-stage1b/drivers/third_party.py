import sys,os,pathlib,subprocess,time,signal,json
home=pathlib.Path.home();sys.path.insert(0,str(home/'lab'));import record_run as rr
pr=next((home/'apps/pr').glob('*.AppImage'));nightly=next((home/'apps/nightly').glob('*.AppImage'))
for p in (pr,nightly):p.chmod(0o700)
an=home/'an';an.mkdir(exist_ok=True);subprocess.run([str(pr),'--appimage-extract'],cwd=an,stdout=subprocess.DEVNULL,check=True);an=an/'squashfs-root'
base_record=rr.Driver.record

def record(self,build,number,fmt):
 name=f'wf-{number}';clip=self.run/'out'/(name+'.mkv');log=self.run/'logs'/(name+'.log')
 state=json.loads(self.mic_state.read_text());source=state['systemSink']+'.monitor'
 cmd=['wf-recorder','--no-dmabuf','--audio='+source,'--codec=ffv1','--audio-codec=pcm_s16le','--framerate=30','--geometry=0,0 960x540','--file='+str(clip)]
 info={'command':cmd,'source':source,'defaultSink':self.pactl('get-default-sink')}
 with log.open('w') as f:
  proc=subprocess.Popen(cmd,env=self.env,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
  info['pid']=proc.pid;time.sleep(18)
  if proc.poll() is None:os.kill(proc.pid,signal.SIGINT)
  try:info['exit']=proc.wait(20)
  except subprocess.TimeoutExpired:os.kill(proc.pid,signal.SIGTERM);info['exit']=proc.wait(10)
 if clip.exists():
  info['av']=self.av_sync(clip);info['motion']=self.motion(clip);info['frame']=self.keep_frame(clip,name,18000000)
 else:info['error']='no third-party clip'
 (self.run/(name+'.json')).write_text(json.dumps(info,indent=1)+'\n')
 result=base_record(self,build,number,fmt);result['thirdParty']=info
 return result
rr.Driver.record=record
args=['--run',str(home/'r'),'--build','nightly='+str(nightly),'--analyzer',str(an),'--video','marker','--rounds','3','--target','region','--rect','0,0,960,540','--format','mp4','--lead','6','--pause-for','0','--pause-at','14','--after','2','--mic','off','--system','tone','--no-notifications','--keep-unpaired','--min-pairs','10','--frames','--vnc-port','0','--video-size','640x360']
(home/'wf-version.txt').write_text(subprocess.run(['wf-recorder','--version'],capture_output=True,text=True).stdout)
rc=rr.main(args);(home/'done').write_text(str(rc)+'\n');sys.exit(rc)
