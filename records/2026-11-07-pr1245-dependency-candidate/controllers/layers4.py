import os,pathlib,sys,json,subprocess
home=pathlib.Path.home().resolve();root=home/'nd';sys.path.insert(0,str(root));os.chdir(root)
from tools.lab import nightly_desktops as n
from tools.lab.desktop_lock import Desktop
p=home/'c1245b';out=p/'out/aurora';config=json.loads((home/'.config/putgd-nightly/config.json').read_text())['builders']['aurora-amd'];os.environ['PATH']=config['toolsBin']+':'+os.environ['PATH']
slot=home/'putgd-lab/locks/tier1-guest.lock.d';owner=json.loads((slot/'owner.json').read_text());session=owner['session'];lock=Desktop(home/'putgd-lab/locks','aurora-amd');n.save(out/'layers4-lock-extend.json',lock.extend(session,45));os.environ['PUTGD_TIER1_SESSION']=session
run=pathlib.Path(owner['run']).resolve();identity=json.loads((p/'identity.json').read_text())
setup=out/'layers-setup';setup.mkdir(mode=0o700);profiles=n.prepare if False else None
from tools.lab.nightly_desktop_guest import prepare
profiles=prepare(run,config['rows'][0],setup)
recipes=['selectors.region_cancel','selectors.region_capture','selectors.region_modes','selectors.recording_selection','selectors.recording_cancel','selectors.bar_options','selectors.bar_recording','selectors.bar_handle','selectors.bar_escape']
n.command([sys.executable,'tools/diagnostics/check_socket_paths.py','--socket','/dev/shm/l1245d/runtime/putgd/session.sock'],log=out/'layers4-sockets.json')
args=[sys.executable,'-m','tools.lab.surface_driver.run','--desktop','aurora-kde-wayland','--host','aurora-amd','--placement','guest','--guest','aurora-kde-wayland','--run',str(run),'--package','appimage','--destination','local','--recipes',','.join(recipes),'--catalog',str(p/'catalog'),'--build',identity['gitCommit'],'--profiles',str(profiles),'--session-root','/dev/shm/l1245d','--out',str(out/'layers4'),'--campaign','pr1245-layer-shell','--coverage',str(out/'layers4-coverage.json')]
r=subprocess.run(args,stdout=(out/'layers4.log').open('x'),stderr=subprocess.STDOUT,timeout=3600)
print('layer_exit',r.returncode,flush=True)
