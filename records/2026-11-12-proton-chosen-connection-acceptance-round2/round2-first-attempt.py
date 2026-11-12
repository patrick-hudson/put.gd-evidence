#!/usr/bin/env python3
# Additive instrumentation; proton_accept.py is the unmodified c0a3ff1c script.
import proton_accept as p
import json, subprocess, time, os, sys
from pathlib import Path
from PIL import Image
checks=[]; states=[]; seen=set(); active=None; pending=False; controlled=False; in_retry=False
orig_follow=p.follow; orig_gone=p.helpers_gone; orig_start=p.App.start

def state(app, reason):
    commands=[['loginctl','list-sessions','--no-legend'],['loginctl','show-seat','seat0','-p','ActiveSession'],['cat','/sys/class/tty/tty0/active'],['loginctl','show-session','auto','-p','LockedHint','-p','Active','-p','State','-p','Type','-p','VTNr'],['xset','-q'],['xprop','-root','_NET_ACTIVE_WINDOW','_NET_CLIENT_LIST_STACKING'],['gdbus','call','--session','--dest','org.freedesktop.ScreenSaver','--object-path','/ScreenSaver','--method','org.freedesktop.ScreenSaver.GetActive'],['wmctrl','-lp'],['ps','-u',str(os.getuid()),'-o','pid=,comm=']]
    rows=[]
    for cmd in commands:
        try:
            r=subprocess.run(cmd,env=app.environment,capture_output=True,text=True,timeout=10)
            rows.append({'command':cmd,'exit':r.returncode,'stdout': ('\n'.join(' '.join(line.split()[:5]) for line in r.stdout.splitlines()) if cmd[0]=='wmctrl' else r.stdout),'stderr':r.stderr})
        except Exception as e: rows.append({'command':cmd,'error':type(e).__name__})
    sid=subprocess.run(['loginctl','show-seat','seat0','-p','ActiveSession','--value'],capture_output=True,text=True).stdout.strip()
    if sid:
        cmd=['loginctl','show-session',sid,'-p','LockedHint','-p','Active','-p','State','-p','Type','-p','VTNr']
        r=subprocess.run(cmd,capture_output=True,text=True)
        rows.append({'command':cmd,'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
    # KWin power state is read-only; unavailable interfaces remain recorded as unavailable.
    if app.desktop=='plasmashell':
        r=subprocess.run(['kscreen-doctor','-o'],env=app.environment,capture_output=True,text=True,timeout=10)
        rows.append({'command':['kscreen-doctor','-o'],'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
    for f in sorted(Path('/sys/class/drm').glob('card*-*/*')):
        if f.name in ('dpms','enabled','status'):
            try: rows.append({'file':str(f),'value':f.read_text().strip()})
            except OSError: pass
    states.append({'at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'reason':reason,'observations':rows})
    (app.work/'display-state.json').write_text(json.dumps(states,indent=2))

def start(app):
    global active
    orig_start(app); active=app
p.App.start=start

def follow(app,operation,invoked,*args,**kwargs):
    global pending,in_retry
    result=orig_follow(app,operation,invoked,*args,**kwargs)
    if any(i.get('bytes')==8388608 for i in result.get('items',[])) and not controlled: pending=True
    black=False
    for f in sorted((app.work/'local-copies').rglob('*.png')):
        if str(f) in seen: continue
        seen.add(str(f)); im=Image.open(f).convert('RGB'); extrema=im.getextrema()
        single=all(a==b for a,b in extrema); isblack=all(a==b==0 for a,b in extrema)
        checks.append({'operationId':operation,'file':str(f.relative_to(app.work)),'bytes':f.stat().st_size,'size':im.size,'extrema':extrema,'singleColour':single,'black':isblack,'acceptancePassed':not single})
        black |= isblack
    (app.work/'capture-checks.json').write_text(json.dumps(checks,indent=2))
    if black:
        state(app,'immediately after black capture '+operation)
        if not in_retry:
            in_retry=True
            t=time.monotonic(); reply,error=app.call('action.invoke',{'action':'desktop'})
            retry={'originalOperationId':operation,'error':error}
            if not error:
                retry['result']={k:v for k,v in follow(app,reply['operationId'],t).items() if not k.startswith('_')}
                orig_gone(15)
            (app.work/'black-immediate-repeat.json').write_text(json.dumps(retry,indent=2)); in_retry=False
    return result
p.follow=follow

def gone(within):
    global pending,controlled
    result=orig_gone(within)
    if pending and not controlled:
        pending=False; controlled=True
        active.stop(); active.remove_entries()
        command=[sys.executable,'proton_accept.py','--app','night-app/squashfs-root' if (Path('night-app/squashfs-root')).exists() else 'night-app','--work','nc','--host',sys.argv[sys.argv.index('--host')+1],'--session',sys.argv[sys.argv.index('--session')+1],'--only','file-1m','file-8m','revoke-all']
        with open('nightly-run.log','x') as log:
            r=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
        (active.work/'nightly-control-exit.json').write_text(json.dumps({'command':command,'exit':r.returncode}))
        active.authorize_capture(); active.start()
    return result
p.helpers_gone=gone
# Capture state immediately before the first screenshot invocation.
orig_call=p.App.call; first=True

def call(app,method,params=None,timeout=130):
    global first
    if method=='action.invoke' and first:
        first=False; state(app,'before first capture')
    return orig_call(app,method,params,timeout)
p.App.call=call
orig_run=p.run
def run(app, tests, only):
    results=orig_run(app,tests,only)
    if not only:
        rows=app.need('history.list',{'limit':100,'offset':0}).get('records',[])
        remaining=[r.get('id') or r.get('historyId') for r in rows if r.get('linkAvailable')]
        (app.work/'revocation-verification.json').write_text(json.dumps({'rows':len(rows),'remainingLinkHistoryIds':remaining,'allRevoked':not remaining},indent=2))
    return results
p.run=run
sys.exit(p.main())
