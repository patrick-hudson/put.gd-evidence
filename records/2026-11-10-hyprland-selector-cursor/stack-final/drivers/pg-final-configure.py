import sys,json,shlex,time
from pathlib import Path
from PIL import Image
sys.path.insert(0,'/home/patrick/work/pg-cd/tools/lab');import lab
name,desktop,label=sys.argv[1:]
assert desktop in ('budgie','hyprland')
r=Path('/home/patrick/work/pg-cd/work/lab-runs')/name;o=r/'accept';o.mkdir(exist_ok=True)
lab.verify_owned_guest(r)
s=lab.cli(r,'settings.get')
actions={a:{'destination':'local','profileId':None,'shortcut':''} for a in ('region','window','desktop','monitor','clipboard','edit')};actions['repeat']={'shortcut':''}
p={'expectedRevision':s['metadata']['acceptedRevision'],'patch':{'actions':actions,'profiles':[],'archive':{'root':'/home/lab/pg-evidence/captures','keepUploads':True},'preferences':{'notifications':False,'regionSelectionMode':'live'}}}
(o/(label+'-settings.json')).write_text(json.dumps(lab.cli(r,'settings.patch',p),indent=2))
# Start a fresh background resident after settings, closing its own dashboard
# and forgetting any region from an earlier matrix cell.
(o/(label+'-configure-quit.json')).write_text(json.dumps(lab.cli(r,'ui.quit'),indent=2));time.sleep(1)
(o/(label+'-configure-start.json')).write_text(json.dumps(lab.start(r),indent=2))
env_script='''import os,shlex
from pathlib import Path
names=('WAYLAND_DISPLAY','HYPRLAND_INSTANCE_SIGNATURE','OMARCHY_PATH','XDG_RUNTIME_DIR','DBUS_SESSION_BUS_ADDRESS','XDG_CURRENT_DESKTOP','XDG_SESSION_TYPE','QT_QPA_PLATFORM','XDG_CONFIG_HOME','XDG_DATA_HOME')
values={n:os.environ[n] for n in names if n in os.environ}
if 'Hyprland' in values.get('XDG_CURRENT_DESKTOP',''):
 for process in Path('/proc').iterdir():
  try:
   if process.stat().st_uid==os.getuid() and (process/'comm').read_text().strip() in ('qs','quickshell'):
    env=dict(x.split('=',1) for x in (process/'environ').read_text().split('\\0') if '=' in x)
    if env.get('OMARCHY_PATH') and env.get('WAYLAND_DISPLAY'):
     values['OMARCHY_PATH']=env['OMARCHY_PATH'];values['WAYLAND_DISPLAY']=env['WAYLAND_DISPLAY'];break
  except (OSError,UnicodeError,ValueError):pass
 if not values.get('OMARCHY_PATH') and Path('/usr/share/omarchy/shell/shell.qml').is_file():values['OMARCHY_PATH']='/usr/share/omarchy'
Path('/tmp/env.sh').write_text(''.join('export '+n+'='+shlex.quote(values[n])+'\\n' for n in names if n in values))
'''
lab.guest_session(r,'python3 -c '+shlex.quote(env_script))
if desktop=='hyprland':
 (o/(label+'-shell-ping.txt')).write_text(lab.guest_session(r,'. /tmp/env.sh; omarchy-shell shell ping'))
(o/(label+'-capabilities.json')).write_text(json.dumps(lab.cli(r,'capabilities'),indent=2))
system='hyprctl systeminfo; hyprctl getoption cursor:no_hardware_cursors' if desktop=='hyprland' else 'rpm -q budgie-desktop labwc gtklock qt6-qtbase; wlr-randr; wlopm'
(o/(label+'-system.txt')).write_text(lab.guest_session(r,system))
for h in (0,1):Image.open(lab.screenshot(r,label+'-configured',h)['path']).save(o/(label+f'-configured-head{h}.png'))
keys=Path('/home/patrick/work/pg-cd/work/hostkeys')/name;keys.mkdir(parents=True,exist_ok=True);(keys/'known_hosts').write_bytes((r/'known_hosts').read_bytes())
print('Configured local-only routes and recorded both guest heads: '+label,flush=True)
