import sys,os,json,subprocess,time,hashlib,shlex
from pathlib import Path
sys.path.insert(0,'/tmp')
# Runs on the builder. Application binaries always come from CI packages.
D,R,K,PKG=sys.argv[1:];ROOT=Path.home()/'work/i1363';os.chdir(ROOT);RUN=ROOT/'work/lab-runs'/R;E=ROOT/'work/acceptance-1363'/R;E.mkdir(parents=True,exist_ok=True)
LAB=['python3','tools/lab/lab.py']
def command(args,name,check=True,timeout=600):
 p=subprocess.run(args,capture_output=True,text=True,timeout=timeout);(E/(name+'.log')).write_text(p.stdout+p.stderr)
 if check and p.returncode:raise RuntimeError(name+' exit '+str(p.returncode))
 return p.stdout
try:
 # vm-launch writes its terminal answer to the launch log; gate on its final JSON.
 for _ in range(150):
  log=(ROOT/'work/lab-runs'/ (R+'-launch.log')).read_text() if (ROOT/'work/lab-runs'/ (R+'-launch.log')).exists() else ''
  if '"status": "booted-not-accepted"' in log:break
  if '"ok": false' in log:raise RuntimeError('launch failed: '+log[-500:])
  time.sleep(2)
 st=json.loads((RUN/'state.json').read_text());port=str(st['ssh_port']);known=str(ROOT/'work/hostkeys'/R/'known_hosts')
 SSH=['ssh','-n','-i',K,'-p',port,'-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile='+known,'lab@127.0.0.1']
 def guest(cmd,name,**kw):return command(SSH+[cmd],name,**kw)
 guest('cat /etc/os-release; loginctl list-sessions --no-legend; uname -r; (dpkg-query -W cinnamon gnome-shell plasma-workspace 2>/dev/null || true); (rpm -q budgie-desktop labwc 2>/dev/null || true); (pacman -Q hyprland omarchy 2>/dev/null || true)','guest-versions')
 (E/'package-identity.json').write_text(json.dumps({'path':PKG,'sha256':hashlib.sha256(Path(PKG).read_bytes()).hexdigest(),'head':'13570fca94df85b799755494d4914fb7009f7e4d','tree':'1e2d35a411dc2f281b3c3414c87503a62476eba8','ciRun':42763770262},indent=2))
 command(LAB+['cli','--run',str(RUN),'--method','ui.quit','--params','{}'],'quit-golden-resident',False)
 time.sleep(2)
 if D=='hyprland':
  guest("python3 -c 'import os,subprocess,shlex,pathlib;p=subprocess.check_output([\"pgrep\",\"-xo\",\"quickshell\"]).decode().strip();e=dict(v.split(b\"=\",1) for v in pathlib.Path(\"/proc/\"+p+\"/environ\").read_bytes().split(b\"\\0\") if b\"=\" in v);pathlib.Path(\"/tmp/env.sh\").write_text(\"\\n\".join(\"export \"+k.decode()+\"=\"+shlex.quote(v.decode()) for k,v in e.items() if k.decode() in [\"WAYLAND_DISPLAY\",\"HYPRLAND_INSTANCE_SIGNATURE\",\"XDG_RUNTIME_DIR\",\"DBUS_SESSION_BUS_ADDRESS\",\"OMARCHY_PATH\",\"XDG_CURRENT_DESKTOP\",\"XDG_SESSION_TYPE\",\"QT_QPA_PLATFORM\"]))'",'hypr-env')
  SCP=['scp','-q','-P',port,'-i',K,'-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile='+known]
  command(SCP+[PKG,'lab@127.0.0.1:/tmp/acceptance.pkg.tar.zst'],'copy-arch');guest('sudo -n pacman -Sy --noconfirm && sudo -n pacman -U --noconfirm /tmp/acceptance.pkg.tar.zst','install-arch')
  import tarfile
  decoder=subprocess.Popen(['zstd','-dc',PKG],stdout=subprocess.PIPE);expected={}
  with tarfile.open(fileobj=decoder.stdout,mode='r|') as archive:
   for member in archive:
    name=member.name.removeprefix('./')
    if member.isfile() and name.startswith('usr/bin/putgd') and '/' not in name[len('usr/bin/'):]:
     digest=hashlib.sha256();stream=archive.extractfile(member)
     for chunk in iter(lambda:stream.read(1024*1024),b''):digest.update(chunk)
     expected['/'+name]=digest.hexdigest()
  decoder.stdout.read();decoder.stdout.close();assert decoder.wait()==0 and expected,expected
  hashes=guest('sha256sum '+shlex.join(list(expected))+'; pacman -Q putgd','verify-arch-binaries');actual={line.split()[1]:line.split()[0] for line in hashes.splitlines() if len(line.split())==2 and len(line.split()[0])==64};assert actual==expected,(actual,expected)
  (RUN/'package.json').write_text(json.dumps({'filename':Path(PKG).name,'sha256':hashlib.sha256(Path(PKG).read_bytes()).hexdigest(),'format':'arch','installedBinarySha256':expected},indent=2))
  command(LAB+['cli','--run',str(RUN),'--method','ui.quit','--params','{}'],'quit-old',False)
  guest('. /tmp/env.sh; setsid -f /usr/bin/putgd --background >/tmp/acceptance-resident.log 2>&1 </dev/null','start-arch')
 elif PKG.endswith('.rpm'):
  SCP=['scp','-q','-P',port,'-i',K,'-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile='+known]
  command(SCP+[PKG,'lab@127.0.0.1:/tmp/acceptance.rpm'],'copy-rpm')
  guest('sudo -n dnf -y install /tmp/acceptance.rpm gnome-shell-extension-appindicator','install-rpm',timeout=1200)
  verify='import sys,json;sys.path.insert(0,"tools/lab");import lab;from pathlib import Path;r=Path('+repr(str(RUN))+');p=Path('+repr(PKG)+');d={"filename":p.name,"sha256":lab.hash_file(p),"format":"rpm","installedBinarySha256":lab.verify_installed_binaries(r,p)};lab.write_json(r/"package.json",d);print(json.dumps(d))'
  command(['python3','-c',verify],'verify-rpm')
  py='import ast,subprocess;v=ast.literal_eval(subprocess.check_output(["gsettings","get","org.gnome.shell","enabled-extensions"],text=True).removeprefix("@as "));v += [x for x in ["putgd@put.gd","appindicatorsupport@rgcjonas.gmail.com"] if x not in v];subprocess.run(["gsettings","set","org.gnome.shell","enabled-extensions",repr(v)],check=True)'
  guest('export XDG_RUNTIME_DIR=/run/user/1000 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus; python3 -c '+shlex.quote(py)+'; sync','enable-extensions')
  command(['python3','/tmp/p1363-qmp.py',R,'system_reset'],'reboot');time.sleep(35)
  guest('gnome-extensions info putgd@put.gd; gnome-extensions info appindicatorsupport@rgcjonas.gmail.com','extension')
  command(LAB+['key','--run',str(RUN),'esc'],'leave-overview',False)
  command(LAB+['start','--run',str(RUN)],'start')
 else:
  if D in ['gnome','kde']:
   hook='sed -i s#http://us.archive.ubuntu.com/ubuntu#https://archive.ubuntu.com/ubuntu#g;s#http://security.ubuntu.com/ubuntu#https://security.ubuntu.com/ubuntu#g /etc/apt/sources.list.d/ubuntu.sources'
   config='Acquire::Languages "none";\n'+''.join('#clear Acquire::IndexTargets::deb::'+target+';\n' for target in ['DEP-11','DEP-11-icons-small','DEP-11-icons','DEP-11-icons-hidpi','DEP-11-icons-large','DEP-11-icons-large-hidpi'])
   hook+='; printf %s '+shlex.quote(config)+' > /etc/apt/apt.conf.d/99putgd-acceptance'
   args=['sudo','-n','/usr/bin/apt-get','-o','APT::Update::Pre-Invoke::='+hook,'-o','Dir::Etc::sourcelist=/dev/null','-o','Dir::Etc::sourceparts=-','-o','APT::Get::List-Cleanup=0','update']
   guest(shlex.join(args),'official-mirror-setup')
  command(LAB+['install','--run',str(RUN),'--appimage' if PKG.endswith('.AppImage') else '--deb',PKG],'install',timeout=1800)
  if D=='gnome':
   guest('sync','sync');command(['python3','/tmp/p1363-qmp.py',R,'system_reset'],'reboot');time.sleep(35);guest('gnome-extensions info putgd@put.gd','extension')
  command(LAB+['start','--run',str(RUN)],'start')
 if D in ['budgie','hyprland']:
  SCP=['scp','-q','-P',port,'-i',K,'-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile='+known]
  command(SCP+['tools/lab/wayland_pointer.py','tools/lab/wayland_toplevels.py','lab@127.0.0.1:/tmp/'],'pointer-copy')
  if D=='budgie':guest('printf "%s\\n" "export XDG_RUNTIME_DIR=/run/user/$(id -u)" "export WAYLAND_DISPLAY=$(basename $(find /run/user/$(id -u) -maxdepth 1 -type s -name wayland-\\* | head -1))" "export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$(id -u)/bus" > /tmp/env.sh','budgie-env')
 command(LAB+['layout','--run',str(RUN)],'layout',D!='budgie')
 if D=='hyprland':
  clients=json.loads(guest('. /tmp/env.sh; hyprctl -j clients','initial-clients'))
  for client in clients:
   if client.get('class')=='putgd-ui':
    xy=client['at'];size=client['size'];guest('. /tmp/env.sh; python3 /tmp/wayland_pointer.py click %d %d --extent 2304 800' % (xy[0]+size[0]-30,xy[1]+28),'close-own-ui')
  time.sleep(12)
 command(['python3','/tmp/p1363-extra.py',R,K,D,'qt'],'qt')
 diag=json.loads(command(LAB+['cli','--run',str(RUN),'--method','diagnostics','--params','{}'],'diagnostics').strip().splitlines()[-1]);diag=diag.get('result',diag);assert diag['build']['gitTree']=='1e2d35a411dc2f281b3c3414c87503a62476eba8',diag.get('build')
 if os.environ.get('P1363_GUI')!='1':
  if D!='hyprland':
   command(LAB+['cli','--run',str(RUN),'--method','ui.show','--params','{"view":"settings"}'],'open-own-ui-before-baseline',False)
   time.sleep(2);command(LAB+['key','--run',str(RUN),'alt','f4'],'close-own-ui-before-baseline',False);time.sleep(2)
  tmp=Path('/tmp')/('p1363-'+R);tmp.mkdir(mode=0o700);os.environ['TMPDIR']=str(tmp)
  command(['python3','/tmp/p1363-checks.py',R,K,D],'checks',False,600)
  if D=='budgie':
   command(['python3','/tmp/p1363-observe-budgie.py',R,K,D],'budgie-lock-observation',False)
  if D=='cinnamon':command(['python3','/tmp/p1363-extra.py',R,K,D,'frozen'],'screenshot-first',False)
 if os.environ.get('P1363_GUI')in ['1','after']:
  (E/'gui-ready.json').write_text(json.dumps({'run':R,'desktop':D,'head':'13570fca9'}));print('GUI READY '+R,flush=True)
  deadline=time.monotonic()+1800
  while not (E/'gui-finished').exists():
   if time.monotonic()>deadline:raise RuntimeError('GUI campaign timed out')
   time.sleep(.5)
 command(LAB+['preflight','--run',str(RUN),'--stage','after-base'],'after-preflight',False)
 print('base finished',D,flush=True)
except Exception as e:
 (E/'failure.txt').write_text(str(e));print('FAILED',D,e,flush=True)
finally:
 # Stop at once after this run; guarded retirement follows evidence export.
 command(LAB+['reset','--run',str(RUN)],'shutdown',False)
 print('stopped',D,flush=True)
