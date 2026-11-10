import os,sys,json,subprocess,time,sqlite3,uuid,copy,struct,zlib
from pathlib import Path
class RunError(RuntimeError):pass
SESSION_VARIABLES = ('DISPLAY', 'XAUTHORITY', 'DBUS_SESSION_BUS_ADDRESS', 'XDG_SESSION_TYPE', 'XDG_CURRENT_DESKTOP',
                     'WAYLAND_DISPLAY', 'XDG_SESSION_DESKTOP', 'DESKTOP_SESSION', 'KDE_FULL_SESSION', 'KDE_SESSION_VERSION',
                     'XDG_DATA_HOME', 'HYPRLAND_INSTANCE_SIGNATURE')
def session_environment():
    """The desktop session's environment for clients started from SSH."""
    uid = os.getuid()
    for process in ('plasmashell', 'gnome-shell', 'cinnamon', 'quickshell', 'budgie-panel'):
        pids = subprocess.run(['pgrep', '-u', str(uid), '-x', process], capture_output=True, text=True).stdout.split()
        if pids:
            break
    else:
        raise RunError('no desktop session process (plasmashell, gnome-shell, cinnamon, quickshell, budgie-panel) for this user')
    pairs = Path('/proc/%s/environ' % pids[0]).read_bytes().decode(errors='replace').split('\0')
    found = dict(pair.split('=', 1) for pair in pairs if '=' in pair)
    runtime = '/run/user/%d' % uid
    env = {'HOME': os.environ['HOME'], 'PATH': os.environ.get('PATH', '/usr/bin:/bin'), 'LANG': found.get('LANG', 'C.UTF-8'),
           'USER': os.environ.get('USER', ''), 'XDG_RUNTIME_DIR': runtime}
    env.update({name: found[name] for name in SESSION_VARIABLES if found.get(name)})
    if env.get('XDG_SESSION_TYPE') == 'wayland' and not env.get('WAYLAND_DISPLAY'):
        shown = subprocess.run(['systemctl', '--user', 'show-environment'], capture_output=True, text=True).stdout
        env.update(line.split('=', 1) for line in shown.splitlines() if line.startswith('WAYLAND_DISPLAY='))
    if env.get('WAYLAND_DISPLAY') and not env['WAYLAND_DISPLAY'].startswith('/'):
        env['WAYLAND_DISPLAY'] = runtime + '/' + env['WAYLAND_DISPLAY']
    env['QT_QPA_PLATFORM'] = 'wayland' if env.get('XDG_SESSION_TYPE') == 'wayland' else 'xcb'
    return env, process
DOC={'schemaVersion': 1, 'actions': {'region': {'destination': 'local', 'profileId': None, 'shortcut': ''}, 'window': {'destination': 'local', 'profileId': None, 'shortcut': ''}, 'desktop': {'destination': 'local', 'profileId': None, 'shortcut': ''}, 'clipboard': {'destination': 'local', 'profileId': None, 'shortcut': ''}, 'edit': {'destination': 'local', 'profileId': None, 'shortcut': ''}, 'record': {'shortcut': ''}}, 'profiles': [], 'archive': {'keepUploads': True, 'root': '/tmp/h396m/files', 'folders': {'images': None, 'videos': None, 'text': None, 'other': None}}, 'naming': {'mode': 'original', 'collisionPolicy': 'rename', 'fileTemplate': '{name}.{ext}', 'captureTemplate': 'Screen-Capture-{yyyy}-{MM}-{dd}-{HH}-{mm}-{ss}.{ext}', 'imageTemplate': 'Image-{yyyy}-{MM}-{dd}-{HH}-{mm}-{ss}.{ext}', 'textTemplate': 'Text-{yyyy}-{MM}-{dd}-{HH}-{mm}-{ss}.{ext}'}, 'limits': {'maxFiles': 100, 'pendingOperations': 8, 'concurrentUploads': 1, 'maxFileBytes': 2147483648, 'maxBatchBytes': 2147483648, 'pendingArtifactBytes': 2147483648, 'clipboardTextBytes': 16777216, 'imagePixels': 100000000, 'imageBytes': 536870912, 'pendingImageBytes': 67108864}, 'retention': {'failedArtifactDays': 7, 'recentActivityLimit': 100, 'previewCacheBytes': 268435456, 'historyRetentionDays': None}, 'preferences': {'notifications': True, 'launchAtLogin': False, 'uploadClipboardBehavior': 'each_link', 'unlockCredentialsAtStartup': False, 'updates': {'check': False}, 'appearance': {'theme': 'dark'}}}
root=Path('/tmp/h396m')
env,desktop=session_environment()
env['PIPEWIRE_RUNTIME_DIR']=env['XDG_RUNTIME_DIR']
for key,sub in [('XDG_CONFIG_HOME','config'),('XDG_DATA_HOME','data'),('XDG_STATE_HOME','state'),('XDG_CACHE_HOME','cache'),('XDG_RUNTIME_DIR','runtime')]:env[key]=str(root/sub)
def cli(method,params={}):
 p=subprocess.run(['putgd-cli',method,json.dumps(params)],env=env,capture_output=True,text=True)
 print(p.stdout,flush=True)
 return json.loads(p.stdout)
if sys.argv[1]=='start':
 root.mkdir(mode=0o700)
 for d in ('config','data','state','cache','runtime','files'):(root/d).mkdir(mode=0o700)
 (root/'config/putgd').mkdir(mode=0o700)
 (root/'config/putgd/config.json').write_text(json.dumps(DOC))
 print(json.dumps({'desktop':desktop,'session':env['XDG_SESSION_TYPE'],'qtPlatform':env['QT_QPA_PLATFORM']}))
 with (root/'resident.log').open('w') as log:
  p=subprocess.Popen(['putgd','--background'],env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=log,start_new_session=True)
 (root/'pid').write_text(str(p.pid));print('pid',p.pid)
elif sys.argv[1]=='cli':cli(sys.argv[2],json.loads(sys.argv[3]) if len(sys.argv)>3 else {})
elif sys.argv[1]=='version':subprocess.run(['putgd-cli','--version-json'],env=env)

elif sys.argv[1]=='seed':
 def chunk(t,b):return struct.pack('>I',len(b))+t+b+struct.pack('>I',zlib.crc32(t+b)&0xffffffff)
 png=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',64,64,8,2,0,0,0))+chunk(b'IDAT',zlib.compress((b'\x00'+b'\x33\x88\xbb'*64)*64))+chunk(b'IEND',b'')
 (root/'synthetic.png').write_bytes(png)
 cli('upload.files',{'paths':[str(root/'synthetic.png')]})
elif sys.argv[1]=='resume':
 with (root/'resident2.log').open('w') as log:p=subprocess.Popen(['putgd','--background'],env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=log,start_new_session=True)
 (root/'pid2').write_text(str(p.pid));print('pid',p.pid)
elif sys.argv[1] in ('capture','input'):
 os.environ.update(env)
 import probe
 ws=probe.x11_windows({'title':'put.gd','owned':True});assert len(ws)==1
 w=ws[0];assert w['states']['active'];assert Path('/proc/'+str(w['pid'])+'/exe').resolve().name=='putgd-ui'
 if sys.argv[1]=='capture':
  subprocess.run(['import','-window',w['window_id'],str(root/(sys.argv[2]+'.png'))],check=True,env=env)
  print(json.dumps({'window':w,'privacy':'owned active app window captured by XID on host'}))
 elif sys.argv[2]=='key':subprocess.run(['xdotool','key','--clearmodifiers','+'.join({'ret':'Return','esc':'Escape','pgdn':'Next','alt':'Alt','right':'Right','left':'Left','shift':'Shift','down':'Down'}.get(n,n) for n in sys.argv[3:])],env=env,check=True)
 elif sys.argv[2] in ('click','double'):subprocess.run(['xdotool','mousemove','--window',w['window_id'],*sys.argv[3:5],'click','--repeat',('2' if sys.argv[2]=='double' else '1'),'--delay','100','1'],env=env,check=True)

elif sys.argv[1]=='resize':
 os.environ.update(env);import probe
 ws=probe.x11_windows({'title':'put.gd','owned':True});assert len(ws)==1 and ws[0]['states']['active']
 subprocess.run(['xdotool','windowsize',ws[0]['window_id'],'1060','680'],env=env,check=True)
