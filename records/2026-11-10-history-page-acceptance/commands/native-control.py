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
DOC={'schemaVersion': 1, 'actions': {'region': {'destination': 'local', 'profileId': None, 'shortcut': ''}, 'window': {'destination': 'local', 'profileId': None, 'shortcut': ''}, 'desktop': {'destination': 'local', 'profileId': None, 'shortcut': ''}, 'clipboard': {'destination': 'local', 'profileId': None, 'shortcut': ''}, 'edit': {'destination': 'local', 'profileId': None, 'shortcut': ''}, 'record': {'shortcut': ''}}, 'profiles': [], 'archive': {'keepUploads': True, 'root': '/tmp/h396k/files', 'folders': {'images': None, 'videos': None, 'text': None, 'other': None}}, 'naming': {'mode': 'original', 'collisionPolicy': 'rename', 'fileTemplate': '{name}.{ext}', 'captureTemplate': 'Screen-Capture-{yyyy}-{MM}-{dd}-{HH}-{mm}-{ss}.{ext}', 'imageTemplate': 'Image-{yyyy}-{MM}-{dd}-{HH}-{mm}-{ss}.{ext}', 'textTemplate': 'Text-{yyyy}-{MM}-{dd}-{HH}-{mm}-{ss}.{ext}'}, 'limits': {'maxFiles': 100, 'pendingOperations': 8, 'concurrentUploads': 1, 'maxFileBytes': 2147483648, 'maxBatchBytes': 2147483648, 'pendingArtifactBytes': 2147483648, 'clipboardTextBytes': 16777216, 'imagePixels': 100000000, 'imageBytes': 536870912, 'pendingImageBytes': 67108864}, 'retention': {'failedArtifactDays': 7, 'recentActivityLimit': 100, 'previewCacheBytes': 268435456, 'historyRetentionDays': None}, 'preferences': {'notifications': True, 'launchAtLogin': False, 'uploadClipboardBehavior': 'each_link', 'unlockCredentialsAtStartup': False, 'updates': {'check': False}, 'appearance': {'theme': 'dark'}}}
root=Path('/tmp/h396k')
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
elif sys.argv[1]=='capture':
 os.environ.update(env)
 import probe,rfb
 from PIL import Image
 windows=probe.kwin_windows()['windows']
 own=[]
 for w in windows:
  try:
   if Path('/proc/'+str(w['pid'])+'/exe').resolve().name=='putgd-ui' and not w['minimized'] and w['normal']:own.append(w)
  except OSError:pass
 assert len(own)==1, 'Need exactly one visible own window'
 w=own[0];assert w['focus'],'App must have focus'
 x,y,width,height=w['content']
 for other in windows:
  if other['stack']>w['stack'] and not other['minimized'] and not other['hidden']:
   a,b,c,d=other['frame']
   assert not (max(x,a)<min(x+width,a+c) and max(y,b)<min(y+height,b+d)), 'Occluded own window'
 r=rfb.RFB(5900)
 try:
  sw,sh,pixels=r.frame()
 finally:r.close()
 assert x>=0 and y>=0 and x+width<=sw and y+height<=sh
 im=Image.frombytes('RGB',(sw,sh),pixels,'raw','BGRX').crop((x,y,x+width,y+height))
 im.save(root/(sys.argv[2]+'.png'))
 print(json.dumps({'window':w,'crop':[x,y,width,height],'privacy':'host checked owned focused unobscured client rectangle'}))

elif sys.argv[1]=='input':
 os.environ.update(env)
 import probe,rfb
 ws=probe.kwin_windows()['windows'];w=next(w for w in ws if w['focus'])
 assert Path('/proc/'+str(w['pid'])+'/exe').resolve().name=='putgd-ui'
 x,y,width,height=w['content'];r=rfb.RFB(5900)
 try:
  if sys.argv[2]=='key':
   import socket
   sock=socket.socket(socket.AF_UNIX);sock.connect(str(root/'input.sock'));f=sock.makefile('rwb');json.loads(f.readline())
   def send(events):
    f.write(json.dumps({'execute':'input-send-event','arguments':{'events':events}}).encode()+b'\n');f.flush();assert 'return' in json.loads(f.readline())
   names=sys.argv[3:]
   try:
    send([{'type':'key','data':{'down':True,'key':{'type':'qcode','data':n}}} for n in names]);time.sleep(.1)
   finally:
    send([{'type':'key','data':{'down':False,'key':{'type':'qcode','data':n}}} for n in reversed(names)]);f.close();sock.close()
  elif sys.argv[2] in ('click','double'):
   a,b=map(int,sys.argv[3:5]);assert 0<a<width and 0<b<height
   import socket,math
   sock=socket.socket(socket.AF_UNIX);sock.connect(str(root/'input.sock'));f=sock.makefile('rwb');json.loads(f.readline())
   def send(events):
    f.write(json.dumps({'execute':'input-send-event','arguments':{'events':events}}).encode()+b'\n');f.flush();assert 'return' in json.loads(f.readline())
   send([{'type':'abs','data':{'axis':'x','value':math.ceil((x+a)*32768/r.width)}},{'type':'abs','data':{'axis':'y','value':math.ceil((y+b)*32768/r.height)}}])
   try:
    for _ in range(2 if sys.argv[2]=='double' else 1):
     send([{'type':'btn','data':{'button':'left','down':True}}]);time.sleep(.05);send([{'type':'btn','data':{'button':'left','down':False}}]);time.sleep(.05)
   finally:send([{'type':'btn','data':{'button':'left','down':False}}]);f.close();sock.close()
  elif sys.argv[2]=='scroll':
   r.pointer_button(x+width-60,y+height//2,'wheel-down',True);r.pointer_button(x+width-60,y+height//2,'wheel-down',False)
 finally:r.close()

elif sys.argv[1]=='resize':
 os.environ.update(env)
 import probe,dbus
 ws=probe.kwin_windows()['windows'];w=next(w for w in ws if w['focus']);assert Path('/proc/'+str(w['pid'])+'/exe').resolve().name=='putgd-ui'
 path=root/'resize.js';path.write_text('const w=workspace.activeWindow;if(w && w.pid=='+str(w['pid'])+')w.frameGeometry={x:300,y:73,width:1060,height:680};')
 bus=dbus.SessionBus();api=dbus.Interface(bus.get_object('org.kde.KWin','/Scripting'),'org.kde.kwin.Scripting');n=api.loadScript(str(path),'history1396-resize',signature='ss');dbus.Interface(bus.get_object('org.kde.KWin','/Scripting/Script'+str(n)),'org.kde.kwin.Script').run();time.sleep(.3);api.unloadScript('history1396-resize');path.unlink()
