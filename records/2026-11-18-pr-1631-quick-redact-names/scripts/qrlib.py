import json,os,subprocess,sys,time
R='/run/user/%d/qr'%os.getuid()
def cli(method,params=None,timeout=90):
    env=dict(os.environ,XDG_RUNTIME_DIR=R)
    p=subprocess.run(['/usr/bin/putgd-cli',method,json.dumps(params or {})],env=env,capture_output=True,text=True,timeout=timeout)
    try: return json.loads(p.stdout)
    except Exception: return {'ok':False,'raw':p.stdout,'err':p.stderr}
def res(method,params=None,**k):
    r=cli(method,params,**k)
    if not r.get('ok'): raise RuntimeError(method+' '+json.dumps(r.get('error'),sort_keys=True)+str(r.get('raw','')))
    return r['result']
def settings_patch(patch):
    g=res('settings.get')
    rev=g['metadata'].get('observedRevision') or g['metadata'].get('revision')
    return res('settings.patch',{'patch':patch,'expectedRevision':rev})
def edit_open(source='desktop',path=None,wait=40):
    p={'source':source}
    if path: p['path']=path
    for i in range(60):
        r=cli('editor.open',p)
        if r.get('ok'): break
        c=r['error']['code']
        if c in ('editor_active','busy_selecting'): time.sleep(1); continue
        raise RuntimeError(json.dumps(r))
    opid=r['result'].get('operationId') or r['result'].get('id')
    t=time.time()
    while time.time()-t<wait:
        x=cli('editor.inspect',{'id':opid})
        if x.get('ok'): return opid,x['result']
        time.sleep(1)
    raise RuntimeError('editor.inspect never ready '+json.dumps(x))
def apply(opid,cmds):
    for i in range(30):
        r=cli('editor.apply',{'id':opid,'commands':cmds},timeout=120)
        if r.get('ok') or r['error']['code']!='editor_starting': return r
        time.sleep(1)
    return r
def inspect(opid): return res('editor.inspect',{'id':opid})
def save(opid,path):
    return res('editor.saveCopy',{'id':opid,'path':path,'overwrite':True})
def cancel(opid): return cli('editor.cancel',{'id':opid})

def overlap(a,b):
    ax,ay,aw,ah=a;bx,by,bw,bh=b
    return max(0,min(ax+aw,bx+bw)-max(ax,bx))*max(0,min(ay+ah,by+bh)-max(ay,by))
def capture_redact(name,cats,source='desktop',path=None,terms=None,patterns=None,keep=False,extra=None):
    O=os.path.expanduser('~/work/qr1618/state/out/')
    opid,ins=edit_open(source,path)
    rep={'name':name,'opid':opid,'size':[ins['width'],ins['height']]}
    save(opid,O+name+'-orig.png')
    words0=[]
    try:
        res('editor.recognize',{'id':opid})
        for i in range(60):
            t_=inspect(opid)['text']
            if t_['state'] in('completed','failed'): words0=t_['words']; break
            time.sleep(1)
    except Exception as e: rep['recognizeErr']=str(e)
    cmd={'op':'redactText','categories':cats}
    if terms is not None: cmd['terms']=terms
    if patterns is not None: cmd['patterns']=patterns
    t=time.time(); r=apply(opid,[cmd]); rep['elapsed']=round(time.time()-t,2)
    rep['apply']=r.get('result') or r.get('error')
    rep['ok']=r.get('ok')
    ins=inspect(opid)
    rep['shapes']=[{k:s.get(k) for k in s if k in('id','kind','rect','suggested')} for s in ins['shapes']]
    words=words0
    rep['words']=len(words); json.dump(words,open(O+name+'-words.json','w'))
    cov=[]
    for s in ins['shapes']:
        r_=s['rect'] if 'rect' in s else None
        if not r_: continue
        cw=[w['text'] for w in words if w['rect'] and overlap(w['rect'],r_)>0.5*w['rect'][2]*w['rect'][3]]
        cov.append({'id':s.get('id'),'suggested':s.get('suggested'),'rect':r_,'words':cw})
    rep['covered']=cov
    rep['panel']=ins.get('view',{}).get('selection')
    if rep['ok']: rep['saved']=save(opid,O+name+'-red.png')
    if not keep: cancel(opid)
    else: rep['kept']=True
    json.dump(rep,open(O+name+'.json','w'),indent=1)
    return rep,ins
