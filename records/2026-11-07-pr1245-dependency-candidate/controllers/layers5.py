import os,pathlib,sys,json,subprocess
home=pathlib.Path.home().resolve();root=home/'nd';sys.path.insert(0,str(root));os.chdir(root)
from tools.lab import nightly_desktops as n
from tools.lab.desktop_lock import Desktop
p=home/'c1245b';out=p/'out/aurora';config=json.loads((home/'.config/putgd-nightly/config.json').read_text())['builders']['aurora-amd'];os.environ['PATH']=config['toolsBin']+':'+os.environ['PATH']
slot=home/'putgd-lab/locks/tier1-guest.lock.d';owner=json.loads((slot/'owner.json').read_text());session=owner['session'];lock=Desktop(home/'putgd-lab/locks','aurora-amd');n.save(out/'layers5-lock-extend.json',lock.extend(session,45));os.environ['PUTGD_TIER1_SESSION']=session
run=pathlib.Path(owner['run']).resolve();identity=json.loads((p/'identity.json').read_text())
from tools.lab import lab
n.save(out/'layers5-probes.json',json.loads(lab.guest_session(run,"python3 -c 'import PyQt6.QtGui,json;print(json.dumps(dict(qtProbe=True)))'")))
info=lab.state(run)
if 'secret_service' in info:
 n.save(out/'stale-guest-secret-selection.json',{'oldBus':info.pop('secret_service'),'reason':'old private guest bus ended at VM restart; host Proton baton already returned'})
 lab.write_json(run/'state.json',info)
recipes=['selectors.region_cancel' ,'selectors.region_capture','selectors.region_modes','selectors.recording_selection','selectors.recording_cancel','selectors.bar_options','selectors.bar_recording','selectors.bar_handle','selectors.bar_escape']
n.command([sys.executable,'tools/diagnostics/check_socket_paths.py','--socket','/dev/shm/l1245e/runtime/putgd/session.sock'],log=out/'layers5-sockets.json')
args=[sys.executable,'-m','tools.lab.surface_driver.run','--desktop','aurora-kde-wayland','--host','aurora-amd','--placement','guest','--guest','aurora-kde-wayland','--run',str(run),'--package','appimage','--destination','local','--recipes',','.join(recipes),'--catalog',str(p/'catalog'),'--build',identity['gitCommit'],'--profiles',str(out/'profiles'),'--session-root','/dev/shm/l1245e','--out',str(out/'layers5'),'--campaign','pr1245-layer-shell','--coverage',str(out/'layers5-coverage.json')]
r=subprocess.run(args,stdout=(out/'layers5.log').open('x'),stderr=subprocess.STDOUT,timeout=3600)
print('layer_exit',r.returncode,flush=True)
