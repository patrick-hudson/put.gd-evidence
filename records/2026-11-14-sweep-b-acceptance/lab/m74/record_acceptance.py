#!/usr/bin/env python3
"""Sweep A1 wrapper around the candidate's unchanged recording driver.
Run only after the nominated CI run succeeds and the desktop lease is held.
"""
import json,os,pathlib,sys,time
sys.path.insert(0,str(pathlib.Path(__file__).parent/'tools/lab'))
import record_run as r
EXPECTED=os.environ.get('SWEEP_EXPECTED_TREE','e12d7610bec4319749a5b55b5411ce3f2b7318c2')
base_session=r.session_environment
original_start=r.Driver.start_resident
original_cli=r.Driver.cli
runtime=pathlib.Path('/tmp')/('sbr'+str(os.getpid()))
runtime.mkdir(mode=0o700)
for suffix in ['putgd/session.sock','wayland-0','pipewire-0']:
 p=runtime/suffix
 assert len(str(p).encode())<=107,(p,len(str(p).encode()))
 print(json.dumps({'socketPath':str(p),'utf8Bytes':len(str(p).encode())}),flush=True)
def session():
 env,desktop=base_session()
 env['PIPEWIRE_RUNTIME_DIR']='/run/user/'+str(os.getuid())
 env['XDG_RUNTIME_DIR']=str(runtime)
 return env,desktop
r.session_environment=session
def cli(self,build,method,params=None,timeout=60):
 result=original_cli(self,build,method,params,timeout)
 with (self.run/'session.jsonl').open('a') as f:
  f.write(json.dumps({'time':time.time(),'method':method,'params':params,'result':result})+'\n')
 if method in ('recording.start','recording.pause','recording.resume','recording.stop'):
  state=original_cli(self,build,'recording.inspect',{'id':params['id']})
  expected={'recording.start':'recording','recording.pause':'paused','recording.resume':'recording','recording.stop':'reviewing'}[method]
  assert state['state']==expected,(method,state)
  self.desktop_frame(self.run/'frames'/(method+'.png'))
 return result
r.Driver.cli=cli
def start(self,build):
 caps=original_start(self,build)
 identity=self.cli(build,'diagnostics')
 assert identity['build']['gitTree']==EXPECTED,identity.get('build')
 (self.run/'build-identity.json').write_text(json.dumps(identity['build'],indent=2))
 return caps
r.Driver.start_resident=start
if __name__ == '__main__': sys.exit(r.main())
