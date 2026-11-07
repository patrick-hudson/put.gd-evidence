import os,pathlib,sys,json
root=pathlib.Path.home().resolve()/'nd';sys.path.insert(0,str(root));os.chdir(root)
from tools.lab import nightly_desktops as n
p=pathlib.Path.home().resolve()/'c1245base';config=json.loads((pathlib.Path.home().resolve()/'.config/putgd-nightly/config.json').read_text())['builders']['aurora-amd'];config=dict(config,host='aurora-amd');config['rows'][0]['live']=False
original=n.retire
def extra(run,out,cells):
 try:
  args=[sys.executable,'-m','tools.lab.surface_driver.run','--desktop','aurora-kde-wayland','--host','aurora-amd','--placement','guest','--guest','aurora-kde-wayland','--run',str(run),'--package','appimage','--destination','local','--recipes','selectors.bar_handle,selectors.recording_selection,selectors.bar_options','--catalog',str(p/'catalog'),'--build',json.loads((p/'identity.json').read_text())['gitCommit'],'--profiles',str(out/'profiles'),'--session-root','/dev/shm/b1245','--out',str(out/'layers-baseline'),'--campaign','pr1245-baseline','--coverage',str(out/'layers-baseline-coverage.json')]
  n.command([sys.executable,'tools/diagnostics/check_socket_paths.py','--socket','/dev/shm/b1245/runtime/putgd/session.sock'],log=out/'baseline-sockets.json')
  n.command(args,log=out/'baseline-layers.log',timeout=1800)
 except Exception as e:(out/'baseline-layers-error.txt').write_text(type(e).__name__+': '+str(e))
 finally:original(run,out,cells)
n.retire=extra
os.environ['PATH']=config['toolsBin']+':'+os.environ['PATH'];n.LOCAL=['file_manager_upload'];n.worker(config,'v26.1105.3986-nightly',json.loads((p/'identity.json').read_text()),p,p/'out')
