import os,pathlib,sys,json,subprocess
home=pathlib.Path.home().resolve();root=home/'nd';sys.path.insert(0,str(root));os.chdir(root)
from tools.lab import nightly_desktops as n
from tools.lab.desktop_lock import Desktop
p=home/'c1245b';out=p/'out/aurora';config=json.loads((home/'.config/putgd-nightly/config.json').read_text())['builders']['aurora-amd'];os.environ['PATH']=config['toolsBin']+':'+os.environ['PATH']
slot=home/'putgd-lab/locks/tier1-guest.lock.d';owner=json.loads((slot/'owner.json').read_text());session=owner['session'];lock=Desktop(home/'putgd-lab/locks','aurora-amd');n.save(out/'layers3-lock-extend.json',lock.extend(session,45));os.environ['PUTGD_TIER1_SESSION']=session
run=pathlib.Path(owner['run']).resolve();identity=json.loads((p/'identity.json').read_text())
from tools.lab import lab
import time
info=lab.state(run);assert not pathlib.Path('/proc/'+str(info['pid'])).exists()
n.save(out/'state-before-restart.json',info)
n.command([sys.executable,'tools/diagnostics/check_socket_paths.py','--socket',str(run/'qmp.sock'),str(run/'vnc.sock')],log=out/'restart-sockets.json')
command=lab.qemu_command(lab.load_profile(info['profile']),run,run/'disk.qcow2',info['ssh_port'],info['vnc_display'],info['acceleration'],info.get('firmware'))
n.save(out/'restart-command.json',command)
r=subprocess.run(command,capture_output=True,text=True,timeout=20);assert r.returncode==0
info['pid']=int((run/'qemu.pid').read_text());lab.write_json(run/'state.json',info)
for attempt in range(120):
 try:lab.ssh(run,'true');break
 except Exception:time.sleep(2)
else:raise RuntimeError('restarted_guest_ssh_timeout')
n.save(out/'restart-preflight.json',lab.guest_preflight(run,apply=True,stage='layers-restart'))
recipes=['selectors.region_cancel','selectors.region_capture','selectors.region_modes','selectors.recording_selection','selectors.recording_cancel','selectors.bar_options','selectors.bar_recording','selectors.bar_handle','selectors.bar_escape']
n.command([sys.executable,'tools/diagnostics/check_socket_paths.py','--socket','/dev/shm/l1245c/runtime/putgd/session.sock'],log=out/'layers3-sockets.json')
args=[sys.executable,'-m','tools.lab.surface_driver.run','--desktop','aurora-kde-wayland','--host','aurora-amd','--placement','guest','--guest','aurora-kde-wayland','--run',str(run),'--package','appimage','--destination','local','--recipes',','.join(recipes),'--catalog',str(p/'catalog'),'--build',identity['gitCommit'],'--profiles',str(out/'profiles'),'--session-root','/dev/shm/l1245c','--out',str(out/'layers3'),'--campaign','pr1245-layer-shell','--coverage',str(out/'layers3-coverage.json')]
r=subprocess.run(args,stdout=(out/'layers3.log').open('x'),stderr=subprocess.STDOUT,timeout=3600)
print('layer_exit',r.returncode,flush=True)
