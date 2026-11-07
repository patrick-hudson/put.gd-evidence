import sys,os,json,subprocess,pathlib
root=pathlib.Path.home()/'nd';sys.path.insert(0,str(root));os.chdir(root)
from tools.lab import nightly_desktops as n
original=n.retire
def extra(run,out,rows):
 try:
  profiles=out/'profiles.json'
  # prepare records its returned profile path in setup logs; default is profiles.json
  print('supplement profile candidates', [str(p) for p in out.glob('*profile*')],flush=True)
  config=json.loads((pathlib.Path.home()/'.config/putgd-nightly/config.json').read_text())['builders']['aurora-amd']
  profiles=n.prepare if False else next(out.glob('*profiles*.json'))
  p=pathlib.Path.home()/'c1245b';identity=json.loads((p/'identity.json').read_text())
  recipes=['selectors.region_cancel','selectors.region_capture','selectors.region_modes','selectors.recording_selection','selectors.recording_cancel','selectors.bar_options','selectors.bar_recording','selectors.bar_handle','selectors.bar_escape']
  target=out/'layers'
  n.command([sys.executable,'tools/diagnostics/check_socket_paths.py','--socket','/dev/shm/l1245/runtime/putgd/session.sock'],log=out/'layers-sockets.json')
  args=[sys.executable,'-m','tools.lab.surface_driver.run','--desktop','aurora-kde-wayland','--host','aurora-amd','--placement','guest','--guest','aurora-kde-wayland','--run',str(run),'--package','appimage','--destination','local','--recipes',*recipes,'--catalog',str(p/'catalog'),'--build',identity['gitCommit'],'--profiles',str(profiles),'--session-root','/dev/shm/l1245','--out',str(target),'--campaign','pr1245-layer-shell','--coverage',str(out/'layers-coverage.json')]
  n.command(args,log=out/'layers.log',timeout=3600)
 except Exception as e:
  (out/'layers-error.txt').write_text(type(e).__name__+': '+str(e))
 finally:original(run,out,rows)
n.retire=extra
n.main()
