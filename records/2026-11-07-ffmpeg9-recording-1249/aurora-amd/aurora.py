import sys,subprocess,time,os,pathlib
sys.path.insert(0,str(pathlib.Path(__file__).parent/'tools/lab'))
import record_run as r
oldopen=r.Driver.open_cover;oldclose=r.Driver.close_cover

def opened(self):
 mode=self.args.video;self.args.video='still'
 report=oldopen(self);self.args.video=mode
 if mode=='still':return report
 if mode=='marker':
  marker=self.run/'marker.mkv';self.helper('--av-marker',marker,60).check_returncode();inp=['-loop','0',str(marker)]
 else:inp=['-f','lavfi','smptebars=size=1280x720:rate=30,scroll=horizontal=0.1']
 env=dict(self.env,SDL_VIDEODRIVER='x11')
 self.player=subprocess.Popen(['ffplay','-loglevel','error','-noborder','-left','320','-top','180','-x','1280','-y','720']+inp,env=env,stdin=subprocess.DEVNULL,stdout=open(self.run/'logs/player.log','w'),stderr=subprocess.STDOUT)
 time.sleep(3);assert self.player.poll() is None
 report.update(video=mode,player='distro ffplay (gtksink unavailable)');return report

def closed(self):
 if getattr(self,'player',None) is not None:
  self.player.terminate();self.player.wait(10)
 oldclose(self)
r.Driver.open_cover=opened;r.Driver.close_cover=closed
sys.exit(r.main())
