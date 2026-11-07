import pathlib,sys,os,json,uuid,subprocess,threading
home=pathlib.Path.home().resolve();root=home/'nd';sys.path.insert(0,str(root));os.chdir(root)
from tools.lab import nightly_desktops as n,lab
from tools.lab.nightly_desktop_guest import install_rpm,prepare
from tools.lab.desktop_lock import Desktop
os.umask(0o077)
base=home/'work/f44-editor-ab-1247';label=sys.argv[1];kind=sys.argv[2];out=base/label;out.mkdir(mode=0o700)
config=json.loads((home/'.config/putgd-nightly/config.json').read_text())['builders']['f44'];config['host']='f44';row=config['rows'][0]
run=root/'work/lab-runs'/('ab'+uuid.uuid4().hex[:7]);session='codex-pr1247-ab';cells={};lock=Desktop(home/'putgd-lab/locks','f44');stop=threading.Event()
def beat():
 while not stop.wait(120):lock.heartbeat(session);lock.extend(session,45)
threading.Thread(target=beat,daemon=True).start()
package=next((base/kind).glob('*.rpm'));sha=n.digest(package);assert sha=={'candidate':'843707167f28708c65c63ec82e3e54d5caacdd0c65e21b85c865205476733851','nightly':'c401e30e4ddd066100fcf6e51c3b4e2e9ca8b97943ea3e67da9d70edf9920423'}[kind]
catalog=home/'c1247/catalog' if kind=='candidate' else base/'nightly/ui-catalog'
try:
 n.save(out/'preflight.json',n.preflight(config));n.command(['python3','tools/diagnostics/check_socket_paths.py','--socket',run/'qmp.sock',run/'vnc.sock','/dev/shm/ab/runtime/putgd/session.sock'],log=out/'sockets.json')
 pins=pathlib.Path(row['knownHosts']).read_text().splitlines();key=next(' '.join(p.split()[1:3]) for p in pins if ' ssh-ed25519 ' in p);known=out/'known_hosts';known.write_text('[127.0.0.1]:22446 '+key+'\n')
 n.command(['python3','tools/lab/lab.py','launch','--profile',row['profile'],'--golden',row['golden'],'--run',run,'--bootstrap-key',row['bootstrapKey'],'--known-hosts',known,'--ssh-port','22446','--vnc-display','46','--timeout','420'],log=out/'launch.log',timeout=600)
 install_rpm(run,package,out);profiles=prepare(run,row,out)
 info=json.loads(lab.ssh(run,'/usr/bin/putgd --version-json'));build=info['gitCommit'];n.save(out/'identity.json',dict(info,packageSha256=sha,run=lab.state(run),driver=n.command(['git','rev-parse','HEAD']).strip()))
 for flow in n.LOCAL:
  recipe='outcomes.'+flow;cells[flow]={'attempts':[]}
  for attempt in (1,2):
   runtime='/dev/shm/a'+uuid.uuid4().hex[:8];name=flow+'-'+str(attempt);target=out/name
   n.command(['python3','tools/diagnostics/check_socket_paths.py','--socket',target/'runtime/putgd/session.sock',runtime+'/runtime/putgd/session.sock'],log=out/(name+'-sockets.json'))
   args=['nice','-n','10','python3','-m','tools.lab.surface_driver.run','--desktop',row['desktop'],'--host','f44','--placement','guest','--guest',row['profile'],'--run',str(run),'--package','rpm','--destination','local','--recipes',recipe,'--catalog',str(catalog),'--build',build,'--profiles',str(profiles),'--session-root',runtime,'--out',str(target),'--campaign','pr1247-editor-ab','--coverage',str(out/(name+'-coverage.json'))]
   try:n.command(args,env=dict(os.environ,PUTGD_TIER1_SESSION=session),log=out/(name+'.log'),timeout=1800)
   except (RuntimeError,subprocess.TimeoutExpired):pass
   observed=n.verdict(target,recipe);cells[flow]['attempts'].append(observed);cells[flow].update(observed);n.save(out/'result.json',dict(package=kind,build=build,cells=cells));print(label,flow,observed['status'],flush=True)
   if observed['green']:break
finally:
 if (run/'state.json').exists():
  if (run/'disk.qcow2').exists():n.retire(run,out,cells)
  lab.reset(run)
 stop.set()
