from pathlib import Path
b=Path('/tmp/p3a')
s=(b/'round2.py').read_text()
s=s.replace('orig_start(app); active=app', '''log=app.work/'resident.log'
    if log.exists():
        n=1
        while (app.work/f'resident-start-{n}.log').exists(): n+=1
        log.rename(app.work/f'resident-start-{n}.log')
    orig_start(app); active=app''')
a=s.index('        if not in_retry:');z=s.index('    return result',a)
s=s[:a]+s[z:]
s=s.replace("    with (app.work/'observed-operations.jsonl')", "    inspect_failures(app,result)\n    with (app.work/'observed-operations.jsonl')")
s=s.replace('if any(i.get(\'bytes\')==8388608',"if sys.argv[sys.argv.index('--host')+1] in ('k72','f44') and any(i.get('bytes')==8388608")
s=s.replace("command=[sys.executable,'proton_accept.py'", "command=[sys.executable,'round3.py'")
s=s.replace("'--only','file-1m','file-8m','revoke-all']", "'--only','file-1m','file-8m','revoke-all']")
s=s.replace("if sys.argv[sys.argv.index('--host')+1] in", "if not getattr(app,'is_control',False) and sys.argv[sys.argv.index('--host')+1] in")
s=s.replace("    orig_start(app); active=app", "    app.is_control=('--only' in sys.argv); orig_start(app); active=app")
s=s.replace("        (active.work/'resident.log').rename(active.work/'resident-before-control.log')", "        # start() rotates every existing log before each launch.")
s=s.replace('    if not only:\n        rows=', '    if not only or "revoke-all" in only:\n        rows=')
s=s.replace("if __name__=='__main__': sys.exit(p.main())", '''def clean(value):
    if isinstance(value,dict): return {k:clean(v) for k,v in value.items() if not any(t in k.lower() for t in ('url','token','password','secret','credential','linkfragment'))}
    if isinstance(value,list): return [clean(v) for v in value]
    if isinstance(value,str):
        import re
        return re.sub(r'https?://[^\\s"<>]+','[address omitted]',value)
    return value

def inspect_failures(app,result):
    for item in result.get('items',[]):
        if item.get('shareStatus') in ('shared','not_requested',None): continue
        if result.get('state')=='cancelled': continue
        entry={'operationId':result['operationId'],'item':item,'phasesFirstSeenAt':result['phasesFirstSeenAt'],'seconds':result['seconds']}
        t=time.monotonic();reply,error=app.call('history.inspectLink',{'id':item['historyId']})
        entry.update(inspectAfterFailureSeconds=round(t-(time.monotonic()-0),3),reply=clean(reply),error=clean(error))
        # Delay is measured from terminal observation, before the request.
        entry['inspectAfterFailureSeconds']=round(t-inspect_failures.terminal,3)
        if not error:
            deadline=time.monotonic()+120
            while time.monotonic()<deadline:
                r,e=app.call('share.inspect',{'id':reply['shareOperationId']})
                if e or r.get('state')!='running':break
                time.sleep(.1)
            entry.update(result=clean(r),inspectError=clean(e))
        with (app.work/'nonshared-inspections.jsonl').open('a') as f:f.write(json.dumps(entry)+'\\n')

_old_inspect=inspect_failures
def inspect_failures(app,result):
    _old_inspect.terminal=time.monotonic()
    return _old_inspect(app,result)
# Function body references this name for the terminal timestamp.
# Set both attributes to the same observed terminal instant.
def inspect_failures(app,result):
    inspect_failures.terminal=time.monotonic()
    return _old_inspect(app,result)

if __name__=='__main__':
    host=sys.argv[sys.argv.index('--host')+1]
    if host in ('d69','m74') and '--only' not in sys.argv:
        command=[sys.executable,'round3.py','--app','night-app/squashfs-root' if Path('night-app/squashfs-root').exists() else 'night-app','--work','nc','--host',host,'--session',sys.argv[sys.argv.index('--session')+1],'--only','file-1m','file-8m','revoke-all']
        with open('nightly-run.log','x') as log: r=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
        Path('nightly-first-exit.json').write_text(json.dumps({'exit':r.returncode,'command':command}))
    sys.exit(p.main())''')
# Track only actual attempted sharing, including failed upload items if app reports failed sharing.
(b/'round3.py').write_text(s)
s=(b/'drive.py').read_text().replace("BASE=P.Path('/tmp/pr1414r2'); ORIG=BASE/'records/2026-11-12-proton-chosen-connection-acceptance'", "BASE=P.Path('/tmp/p3a'); ORIG=BASE")
s=s.replace("'p1414-ec6-'","'p1414-r3-'").replace('proton-round2','proton-round3').replace('pr1414r2','p3a').replace('pecr2','p3a').replace('round2.py','round3.py')
s=s.replace("out.mkdir(exist_ok=(host=='f44' and not (out/'run.log').exists()))",'out.mkdir()')
s=s.replace("with (out/'raw.tar').open('wb') as f:remote('cd ~/work/p3a && tar -cf - pr nc nightly-run.log',stdout=f)","with (out/'raw.tar').open('wb') as f:remote(\"cd ~/work/p3a && tar --exclude=local-copies --exclude=payloads --exclude=config --exclude=data --exclude=cache -cf - pr nc nightly-run.log\",stdout=f)")
s=s.replace("stop.set();t.join()", "stop.set();t.join()")
(b/'drive3.py').write_text(s)
