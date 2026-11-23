import configparser, platform, hashlib, json, os, re, shlex, socket, struct, subprocess as sp, sys, time, threading, traceback
from pathlib import Path
from PIL import Image, ImageChops
from rfb import RFB
from kwin_entries import sync_entries
from host_input import serve as serve_input

host=sys.argv[1]
root=Path(sys.argv[2]).resolve()
tree='941d212d6aba88311cd269955e631ccf7e09bb0a'
os.umask(0o077)
runtime=Path('/run/user')/str(os.getuid())
env=dict(os.environ)
compositor={'m74':'cinnamon','f44':'gnome-shell'}.get(host,'plasmashell')
pids=sp.check_output(['pgrep','-u',str(os.getuid()),'-x',compositor],text=True).split()
assert len(pids)==1,pids
pairs=dict(z.split(b'=',1) for z in Path('/proc',pids[0],'environ').read_bytes().split(b'\0') if b'=' in z)
for k in ('DISPLAY','XAUTHORITY','DBUS_SESSION_BUS_ADDRESS','XDG_SESSION_TYPE','XDG_CURRENT_DESKTOP','WAYLAND_DISPLAY','XDG_SESSION_DESKTOP','DESKTOP_SESSION','KDE_FULL_SESSION','KDE_SESSION_VERSION'):
    env.pop(k,None)
    if k.encode() in pairs: env[k]=pairs[k.encode()].decode()
if host!='m74' and not env.get('WAYLAND_DISPLAY'):
    env['WAYLAND_DISPLAY']=next(s.split('=',1)[1] for s in sp.check_output(['systemctl','--user','show-environment'],text=True).splitlines() if s.startswith('WAYLAND_DISPLAY='))
if host!='m74':
    env['WAYLAND_DISPLAY']=str(runtime/env['WAYLAND_DISPLAY'])
env['XDG_RUNTIME_DIR']=str(runtime)
env.setdefault('DBUS_SESSION_BUS_ADDRESS','unix:path='+str(runtime/'bus'))
native=env.copy()
env.update(PIPEWIRE_RUNTIME_DIR=str(runtime),QT_QPA_PLATFORM='xcb' if host=='m74' else 'wayland')
env.update({f'XDG_{k}_HOME':str(root/k.lower()) for k in ('CONFIG','DATA','CACHE','STATE')})
env['XDG_RUNTIME_DIR']=str(root/'runtime')
for name in ('config','data','cache','state','runtime','extract'):
    (root/name).mkdir(exist_ok=True)
sock=root/'runtime/putgd/session.sock'
insock=root/'input.sock'
for path in (sock,insock):
    assert len(os.fsencode(path))<=107,path
log=(root/'resident.log').open('a')
app=None
cli_env=env
fixture=None
inputproc=None
cmd=None
port=5901 if host=='f44' else 5900
mode='appimage'
shadow_path=None
def out(name,value):
    (root/name).write_text(json.dumps(value,indent=2)+'\n')
    return value
def cli(method,params=None,timeout=45):
    result=sp.run([str(cmd),method,'--params-stdin'],input=json.dumps(params or {}),env=cli_env,capture_output=True,text=True,timeout=timeout)
    try:
        response=json.loads(result.stdout)
    except ValueError:
        raise RuntimeError(f'{method}: exit {result.returncode}: {result.stderr[-600:]}') from None
    if not response.get('ok'):
        e=response.get('error',{})
        raise RuntimeError(f'{method} {params or {}}: {e.get("code")} {e.get("message")}')
    return response.get('result',{})
def wait_for(fn, timeout=10):
    deadline=time.monotonic()+timeout
    while True:
        val=fn()
        if val: return val
        if time.monotonic()>deadline: raise TimeoutError(fn.__name__)
        time.sleep(.05)
def stop(proc):
    if proc and proc.poll() is None:
        proc.terminate()
        try: proc.wait(8)
        except sp.TimeoutExpired:
            proc.kill()
            proc.wait(8)
def quit_app():
    global app
    if app is None: return
    try: cli('ui.quit',timeout=7)
    except Exception: pass
    try: app.wait(12)
    except sp.TimeoutExpired: stop(app)
    if host not in ('m74','f44') and mode.endswith('appimage'):
        old=dict(os.environ)
        try:
            os.environ.update(env)
            sync_entries(str(root),str(sock),cleanup=True)
        finally:
            os.environ.clear();os.environ.update(old)
    app=None
def launch(kind='appimage'):
    global app,cmd,mode,cli_env
    assert app is None and not sock.exists()
    mode=kind
    if kind=='appimage':
        image=root/('direct.AppImage' if (root/'direct.AppImage').exists() else 'candidate.AppImage')
    elif kind=='nightly-appimage':
        image=root/'nightly.AppImage'
    else:
        image='/usr/bin/putgd'
    app=sp.Popen([str(image),'--background'],env=env,stdout=log,stderr=log,stdin=sp.DEVNULL)
    wait_for(sock.exists,25)
    peer=socket.socket(socket.AF_UNIX)
    with peer:
        peer.connect(str(sock))
        pid,uid,_=struct.unpack('3i',peer.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12))
    assert uid==os.getuid()
    executable=Path('/proc',str(pid),'exe').resolve(strict=True)
    cmd=executable.with_name('putgd-cli')
    cli_env=env.copy()
    if kind.endswith('appimage'):
        cli_env['LD_LIBRARY_PATH']=str(executable.parents[1]/'lib')+':'+str(executable.parents[1]/'lib/putgd')
    if host not in ('f44','m74') and kind.endswith('appimage'):
        old=dict(os.environ)
        try:
            os.environ.update(env)
            sync_entries(str(root),str(sock))
        finally:
            os.environ.clear();os.environ.update(old)
    ident=cli('diagnostics')['build']
    cap=cli('capabilities')
    observed=out(f'identity-{kind}.json',dict(build=ident,cpus=int(sp.check_output(['nproc'])),cpuModel=next(x.split(':',1)[1].strip() for x in Path('/proc/cpuinfo').read_text().splitlines() if x.startswith('model name')),os=platform.freedesktop_os_release()['PRETTY_NAME'],desktop=env.get('XDG_CURRENT_DESKTOP'),session=env.get('XDG_SESSION_TYPE'),socketBytes=len(os.fsencode(sock)),textCapabilities=cap.get('text')))
    if kind in ('appimage','deb'): assert ident['gitTree']==tree,ident
    return observed

def control(value):
    temp=root/'fixture-next'
    temp.write_text(value)
    temp.replace(root/'fixture-mode')
def rfb():
    return RFB(port,timeout=4)
def frame():
    with_rfb=rfb()
    try: w,h,pixels=with_rfb.frame()
    finally: with_rfb.close()
    return Image.frombytes('RGB',(w,h),pixels,'raw','BGRX')
def backdrop():
    f=frame()
    solid=Image.new('RGB',f.size,(255,0,255))
    matches=sum(n for n,color in f.getcolors(f.width*f.height) if color==(255,0,255))
    assert matches >= f.width*f.height*.96, f'fullscreen synthetic cover fraction {matches/(f.width*f.height):.3f}'
    return f.size
def shot(name):
    f=frame()
    diff=ImageChops.difference(f,Image.new('RGB',f.size,(255,0,255))).convert('L')
    diff=diff.point(lambda v: 255 if v>18 else 0)
    xm,ym=f.width//2,f.height//2
    assert diff.getpixel((xm,ym)), 'no settings-shaped region at screen center'
    def interval(limit, at, position):
        lo=hi=position
        while lo>0 and at(lo-1): lo-=1
        while hi+1<limit and at(hi+1): hi+=1
        return lo,hi+1
    x0,x1=interval(f.width,lambda x:diff.getpixel((x,ym)),xm)
    y0,y1=interval(f.height,lambda y:diff.getpixel((xm,y)),ym)
    assert x1-x0>500 and y1-y0>450 and x0>0 and x1<f.width, (x0,y0,x1,y1)
    box=(x0,y0,x1,y1)
    f.crop(box).save(root/(name+'.png'))
    return box
input_socket=None
input_stream=None
def input_cmd(events):
    global input_socket,input_stream
    if input_stream is None:
        input_socket=socket.socket(socket.AF_UNIX)
        input_socket.connect(str(insock))
        input_stream=input_socket.makefile('rwb')
        input_stream.readline()
        input_stream.write(b'{"execute":"qmp_capabilities"}\n')
        input_stream.flush()
        assert 'return' in json.loads(input_stream.readline())
    req={'execute':'input-send-event','arguments':{'events':events}}
    input_stream.write(json.dumps(req).encode()+b'\n')
    input_stream.flush()
    reply=json.loads(input_stream.readline())
    assert 'return' in reply,reply
def mouse(x,y,down=None,button='left'):
    if host=='m74':
        args=['xdotool','mousemove',str(x),str(y)]
        if down is not None: args+=['mousedown' if down else 'mouseup','1']
        sp.run(args,env=native,check=True,timeout=3)
    else:
        size=pointer_size
        events=[{'type':'abs','data':{'axis':axis,'value':round(v*32767/(lim-1))}} for axis,v,lim in [('x',x,size[0]),('y',y,size[1])]]
        if down is not None: events.append({'type':'btn','data':{'button':button,'down':down}})
        input_cmd(events)
def click(x,y):
    mouse(x,y)
    time.sleep(.08)
    mouse(x,y,True)
    time.sleep(.06)
    mouse(x,y,False)
def key(c):
    if host=='m74':
        sp.run(['xdotool','key','--delay','0',{'esc':'Escape','close':'alt+F4'}.get(c,c)],env=native,check=True,timeout=3)
    else:
        sequence=[('alt',True),('f4',True),('f4',False),('alt',False)] if c=='close' else [(c,True),(c,False)]
        for code,down in sequence:
            input_cmd([{'type':'key','data':{'down':down,'key':{'type':'qcode','data':code}}}])
def fixture_start():
    global fixture,inputproc,pointer_size
    control('cover')
    fixture=sp.Popen([sys.executable,str(root/'fixture.py'),str(root)],env=native,stdout=log,stderr=log)
    if host!='m74':
        inputproc=sp.Popen(['sudo','-n',sys.executable,str(root/'host_input.py'),'serve','--socket',str(insock),'--user','patrick'],stdout=log,stderr=log)
        wait_for(insock.exists)
        time.sleep(.6)
    if host=='f44':
        f=frame()
        pointer_size=f.size
        mid=(f.width//2,f.height//2)
        if f.getpixel(mid)==(255,0,255):
            click(*mid)
    for _ in range(12):
        time.sleep(.3)
        try:
            pointer_size=backdrop()
            break
        except AssertionError as e: failure=str(e)
    else: raise RuntimeError(failure)
    return pointer_size

def setting():
    settings=cli('settings.get')
    values=settings['document'].get('preferences',{})
    paths=list((root/'config').glob('*/config.json'))
    disk=json.loads(paths[0].read_text()).get('preferences',{}) if paths else {}
    return dict(present='unhingedMode' in values,value=values.get('unhingedMode'),diskPresent='unhingedMode' in disk,diskValue=disk.get('unhingedMode'))
def patch(on):
    s=cli('settings.get')
    cli('settings.patch',dict(patch=dict(preferences=dict(unhingedMode=on)),expectedRevision=s['metadata']['observedRevision']))
    return setting()
def settings_open():
    control('cover')
    time.sleep(.3)
    cli('ui.show',{'view':'settings'})
    cli('ui.diagnostics',{'action':'setDesktopDetails','enabled':False})
    time.sleep(.75)
    return shot('settings-probe')
def settings_click(x,y,label):
    click(x,y); time.sleep(.85)
    saved=out('setting-'+label+'.json',setting())
    return dict(settings=saved,box=shot('settings-'+label))
def children():
    found=[]
    for p in Path('/proc').iterdir():
        if not p.name.isdigit(): continue
        try:
            if (p/'comm').read_text().strip()!='putgd-ocr': continue
            state=(p/'status').read_text()
            parent=int(re.search(r'^PPid:\s*(\d+)',state,re.M)[1])
            pe=(Path('/proc')/str(parent)/'environ').read_bytes().split(b'\0')
            if b'XDG_RUNTIME_DIR='+os.fsencode(env['XDG_RUNTIME_DIR']) in pe:
                found.append((int(p.name),int(re.search(r'^Threads:\s*(\d+)',state,re.M)[1])))
        except (FileNotFoundError,ProcessLookupError,PermissionError): continue
    return found
fixed='abcdefghijklmnopqrstuvwxyz0123456789abcd'
def ocr(label):
    control('tokens')
    time.sleep(.6)
    f=frame()
    w,h=f.size
    expected=Image.open(root/'tokens.png').convert('RGB').resize((w-16,h-16),Image.Resampling.BILINEAR)
    actual=f.crop((8,8,w-8,h-8)).resize((40,24))
    expect=expected.resize((40,24))
    delta=ImageChops.difference(actual,expect)
    assert sum(sum(rgb) for rgb in delta.getdata())/(40*24*3)<12,'synthetic OCR fixture is not the visible frame'
    op=cli('text.recognize',{'source':'region','copy':True})['operationId']
    time.sleep(.55)
    samples=[]
    done=threading.Event()
    errors=[]
    onset=[]
    def sample():
        while not done.is_set():
            t=time.monotonic()
            p=children()
            samples.append((t,p))
            if p and not onset:
                onset.append(t)
            done.wait(max(0,.2-(time.monotonic()-t)))
    thread=threading.Thread(target=sample)
    thread.start()
    try:
        mouse(14,14); time.sleep(.10)
        mouse(14,14,True)
        for i in range(1,12):
            time.sleep(.025)
            mouse(14+(w-29)*i//11,14+(h-64)*i//11)
        mouse(w-15,h-50,False)
        release=time.monotonic()
        wait_for(lambda:onset,5)
        focus=root/f'input-{label}.focused'
        focus.unlink(missing_ok=True)
        control('input-'+label)
        wait_for(focus.exists,1.5)
        path=root/f'input-{label}.csv'
        sent=[]
        for i,c in enumerate(fixed):
            if i: time.sleep(max(0,sent[0]+i*.05-time.monotonic()))
            sent.append(time.monotonic())
            key(c)
        time.sleep(.20)
        entries=path.read_text().splitlines()[1:]
        times=[float(r.split(',',1)[0]) for r in entries]
        actual=entries[-1].split(',',1)[1] if entries else ''
        worst=max((b-a for a,b in zip([sent[0],*times],times)),default=None)
        limit=time.monotonic()+35
        while True:
            result=cli('text.inspect',{'id':op})
            if result.get('state') in ('completed','cancelled','failed'): break
            if time.monotonic()>limit: raise TimeoutError('text.inspect: '+result.get('state',''))
            time.sleep(.15)
        job={k:result.get(k) for k in ('state','error','truncated','characterCount','copyStatus','timings','banded')}
        job['sha256']=hashlib.sha256(result['text'].encode()).hexdigest() if 'text' in result else None
        if result.get('copyStatus')=='copied':
            clipcmd=['xclip','-selection','clipboard','-o'] if host=='m74' else ['wl-paste','--no-newline','--type','text']
            cp=sp.run(clipcmd,env=native,capture_output=True,timeout=3)
            job['clipboardSha256']=hashlib.sha256(cp.stdout).hexdigest() if cp.returncode==0 else None
        job.update(id=op,release=release,sentMonotonic=sent,received=len(actual),lost=max(0,len(fixed)-len(actual)),inputMatches=actual==fixed,worstGapMs=round(worst*1000,2) if worst is not None else None,selected=[14,14,w-15,h-50])
    finally:
        done.set();thread.join()
        out('threads-'+label+'.json',samples)
        control('cover')
    nonempty=[t for t,p in samples if p]
    job['maxThreads']=max((n for _,p in samples for _,n in p),default=0)
    job['receivedDuringHelperSamples']=sum(nonempty[0]<=t<=nonempty[-1] for t in times) if nonempty else 0
    return out('ocr-'+label+'.json',job)
def editor(label='candidate'):
    op=cli('editor.open',{'source':'file','path':str(root/'tokens.png')})['operationId']
    try:
        def inspect():
            try: return cli('editor.inspect',{'id':op},timeout=5)
            except RuntimeError: return None
        state=wait_for(inspect,15)
        assert state
        result=cli('editor.apply',{'id':op,'commands':[{'op':'redactText','categories':['email','key']}]},timeout=45)
        return out('editor-'+label+'.json',dict(id=op,inspectOpened=True,counts=result.get('counts'),created=len(result.get('created',[])),setting=setting()))
    finally:
        cli('editor.cancel',{'id':op})

actions={'point':click,'start':fixture_start,'launch':launch,'quit':quit_app,'settings':settings_open,'setting':setting,'click':settings_click,'patch':patch,'ocr':ocr,'editor':editor,'shot':shot,'key':key}
def run_action(req):
    action,*args=req
    if action=='end': return None
    return actions[action](*args)
try:
    for line in sys.stdin:
        try:
            req=json.loads(line)
            result=run_action(req)
            print(json.dumps(dict(ok=True,result=result)),flush=True)
            if req[0]=='end':break
        except Exception as e:
            print(json.dumps(dict(ok=False,error=str(e),trace=traceback.format_exc())),flush=True)
finally:
    try: quit_app()
    finally:
        if input_stream: input_stream.close()
        if input_socket: input_socket.close()
        stop(inputproc)
        if fixture:
            control('exit')
            try: fixture.wait(3)
            except sp.TimeoutExpired: stop(fixture)
