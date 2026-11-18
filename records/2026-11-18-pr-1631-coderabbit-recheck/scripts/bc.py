import sys,json,threading,subprocess,time;sys.path.insert(0,'/home/patrick/work/qr1618/bin')
from qrlib import *
O=os.path.expanduser('~/work/qr1618/state/out/')
mode=sys.argv[1]
def procs():
    out=subprocess.run(['ps','-eo','pid,ppid,args','--no-headers'],capture_output=True,text=True).stdout
    r=[]
    for l in out.splitlines():
        p=l.split(None,2)
        if len(p)>=3: r.append((int(p[0]),int(p[1]),p[2]))
    return r
def editor_pid():
    for pid,pp,a in procs():
        if 'putgd-ui' in a.split()[0] and '--edit-image' in a: return pid
def children(pid):
    try:
        t=os.listdir(f'/proc/{pid}/task'); ch=set()
        for x in t:
            try: ch|=set(int(c) for c in open(f'/proc/{pid}/task/{x}/children').read().split())
            except Exception: pass
        return ch
    except Exception: return set()
def cmd(pid):
    try: return open(f'/proc/{pid}/cmdline','rb').read().replace(b'\0',b' ').decode()[:120]
    except Exception: return None
opid,ins=edit_open('desktop')
time.sleep(1.5)
ep=editor_pid(); print('editor pid',ep,'resident ppid',[pp for pid,pp,a in procs() if pid==ep])
log={'mode':mode,'editor_pid':ep}
seen={}   # child pid -> (first seen t, cmd)
stop=False; gaps=[]
def sampler():
    t0=time.time()
    while not stop:
        for c in children(ep):
            if c not in seen: seen[c]=(round(time.time()-t0,3),cmd(c))
        time.sleep(0.005)
def poller():
    last=time.time()
    while not stop:
        t=time.time(); x=cli('editor.inspect',{'id':opid}); d=time.time()-t
        gaps.append(round(d,3)); time.sleep(0.1)
ts=[threading.Thread(target=sampler),threading.Thread(target=poller)]
[t.start() for t in ts]
cats=['email','phone','ip','card','key','name','list']
if mode in('A','C'):
    t=time.time(); r=apply(opid,[{'op':'redactText','categories':cats}]); el=time.time()-t
    stop=True; [t_.join() for t_ in ts]
    i=inspect(opid)
    log.update({'apply_s':round(el,2),'ok':r.get('ok'),'counts':(r.get('result') or {}).get('counts'),'skippedPatterns':(r.get('result') or {}).get('skippedPatterns'),'error':r.get('error') if not r.get('ok') else None,
      'inspect_polls':len(gaps),'inspect_max_s':max(gaps) if gaps else None,'inspect_gaps_over_0.5s':[g for g in gaps if g>0.5],'children_seen':{str(k):v for k,v in seen.items()},
      'shapes':[(s['id'],s.get('suggested'),s['rect']) for s in i['shapes']]})
    save(opid,O+f'r{mode}-red.png')
    log['panel']=i['view'].get('message') or i['view'].get('selection')
    cancel(opid)
elif mode=='B':
    res_box={}
    th=threading.Thread(target=lambda:res_box.setdefault('r',apply(opid,[{'op':'redactText','categories':cats}])))
    th.start(); helper=None; t0=time.time()
    while time.time()-t0<10 and helper is None:
        for c in children(ep):
            a=cmd(c)
            if a and '--match-patterns' in a:
                helper=(c,a); break
        time.sleep(0.003)
    log['helper']=helper
    if helper:
        log['helper_found_after_s']=round(time.time()-t0,3)
        t1=time.time(); c=cli('editor.cancel',{'id':opid}); log['cancel_ok']=c.get('ok')
        gone=None
        while time.time()-t1<6:
            if not os.path.exists(f'/proc/{helper[0]}'): gone=round(time.time()-t1,3); break
            time.sleep(0.02)
        log['helper_gone_after_s']=gone
        try: os.kill(helper[0],0); log['kill0']='still alive'
        except ProcessLookupError: log['kill0']='ProcessLookupError (gone)'
        time.sleep(1)
        log['children_of_editor_after']=sorted(children(ep)); log['editor_alive']=os.path.exists(f'/proc/{ep}')
        log['match_patterns_procs_after']=[(p,a[:80]) for p,pp,a in procs() if '--match-patterns' in a]
    stop=True; [t_.join() for t_ in ts]
    th.join(timeout=10); log['apply_result_after_cancel']=json.dumps(res_box.get('r'))[:200]
cancel(opid)
print(json.dumps(log,indent=1)); json.dump(log,open(O+f'r{mode}-log.json','w'),indent=1)
