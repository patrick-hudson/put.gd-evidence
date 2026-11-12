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
    log=app.work/'resident.log'
    if log.exists():
        n=1
        while (app.work/f'resident-start-{n}.log').exists(): n+=1
        log.rename(app.work/f'resident-start-{n}.log')
    app.is_control=('--only' in sys.argv); orig_start(app); active=app
p.App.start=start

def follow(app,operation,invoked,*args,**kwargs):
    global pending,in_retry
    result=orig_follow(app,operation,invoked,*args,**kwargs)
    inspect_failures(app,result)
    with (app.work/'observed-operations.jsonl').open('a') as log: log.write(json.dumps({k:v for k,v in result.items() if not k.startswith('_')})+'\n')
    if not getattr(app,'is_control',False) and sys.argv[sys.argv.index('--host')+1] in ('k72','f44') and any(i.get('bytes')==8388608 for i in result.get('items',[])) and not controlled: pending=True
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
    return result
p.follow=follow

def gone(within):
    global pending,controlled
    result=orig_gone(within)
    if pending and not controlled:
        pending=False; controlled=True
        active.stop(); active.remove_entries()
        command=[sys.executable,'round3.py','--app','night-app/squashfs-root' if (Path('night-app/squashfs-root')).exists() else 'night-app','--work','nc','--host',sys.argv[sys.argv.index('--host')+1],'--session',sys.argv[sys.argv.index('--session')+1],'--only','file-1m','file-8m','revoke-all']
        with open('nightly-run.log','x') as log:
            r=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
        (active.work/'nightly-control-exit.json').write_text(json.dumps({'command':command,'exit':r.returncode}))
        # start() rotates every existing log before each launch.
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
    if not only or "revoke-all" in only:
        rows=app.need('history.list',{'limit':100,'offset':0}).get('records',[])
        remaining=[r.get('id') or r.get('historyId') for r in rows if r.get('linkAvailable')]
        (app.work/'revocation-verification.json').write_text(json.dumps({'rows':len(rows),'remainingLinkHistoryIds':remaining,'allRevoked':not remaining},indent=2))
    return results
p.run=run
def clean(value):
    if isinstance(value,dict): return {k:clean(v) for k,v in value.items() if not any(t in k.lower() for t in ('url','token','password','secret','credential','linkfragment'))}
    if isinstance(value,list): return [clean(v) for v in value]
    if isinstance(value,str):
        import re
        return re.sub(r'https?://[^\s"<>]+','[address omitted]',value)
    return value

def inspect_failures(app,result):
    for item in result.get('items',[]):
        if item.get('shareStatus') in ('shared','not_requested',None): continue
        if result.get('state')=='cancelled': continue
        entry={'operationId':result['operationId'],'item':item,'phasesFirstSeenAt':result['phasesFirstSeenAt'],'seconds':result['seconds']}
        t=time.monotonic();reply,error=app.call('history.inspectLink',{'id':item['historyId']})
        entry.update(reply=clean(reply),error=clean(error))
        # Delay is measured from terminal observation, before the request.
        entry['inspectAfterFailureSeconds']=round(t-inspect_failures.terminal,3)
        if not error:
            deadline=time.monotonic()+120
            while time.monotonic()<deadline:
                r,e=app.call('share.inspect',{'id':reply['shareOperationId']})
                if e or r.get('state')!='running':break
                time.sleep(.1)
            entry.update(result=clean(r),inspectError=clean(e))
        with (app.work/'nonshared-inspections.jsonl').open('a') as f:f.write(json.dumps(entry)+'\n')

_old_inspect=inspect_failures
def inspect_failures(app,result):
    inspect_failures.terminal=time.monotonic()
    return _old_inspect(app,result)

if __name__=='__main__':
    host=sys.argv[sys.argv.index('--host')+1]
    if host in ('d69','m74') and '--only' not in sys.argv:
        command=[sys.executable,'round3.py','--app','night-app/squashfs-root' if Path('night-app/squashfs-root').exists() else 'night-app','--work','nc','--host',host,'--session',sys.argv[sys.argv.index('--session')+1],'--only','file-1m','file-8m','revoke-all']
        with open('nightly-run.log','x') as log: r=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
        Path('nightly-first-exit.json').write_text(json.dumps({'exit':r.returncode,'command':command}))
    sys.exit(p.main())
