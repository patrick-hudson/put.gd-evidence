import sys,json;sys.path.insert(0,'/home/patrick/work/qr1618/bin')
import qrlib; qrlib.R='/run/user/%d/qa'%os.getuid() if False else None
import os,subprocess,time
os.environ['LD_LIBRARY_PATH']=os.path.expanduser('~/work/qr1618/rpmx/usr/lib64/putgd')
CLI=os.path.expanduser('~/work/qr1618/rpmx/usr/bin/putgd-cli')
def cli(m,p):
    env=dict(os.environ,XDG_RUNTIME_DIR='/run/user/%d/qa'%os.getuid())
    o=subprocess.run([CLI,m,json.dumps(p)],env=env,capture_output=True,text=True).stdout
    return json.loads(o)
spec=json.load(open(os.path.expanduser('~/work/qr1618/ann/annspec.json')))
IN=os.path.expanduser('~/work/qr1618/ann/in/'); OUT=os.path.expanduser('~/work/qr1618/ann/out/')
os.makedirs(OUT,exist_ok=True)
for name,s in spec.items():
    for i in range(60):
        r=cli('editor.open',{'source':'file','path':IN+name+'.png'})
        if r['ok']: break
        time.sleep(1)
    else: print(name,'open failed',r); continue
    op=r['result'].get('operationId') or r['result'].get('id')
    cmds=s['cmds']+[{"op":"crop","rect":s['crop']}]
    for i in range(60):
        r=cli('editor.apply',{'id':op,'commands':cmds})
        if r['ok'] or r['error']['code']!='editor_starting': break
        time.sleep(1)
    print(name,'apply',r['ok'],r.get('error'))
    r=cli('editor.saveCopy',{'id':op,'path':OUT+name+'.png','overwrite':True}); print(name,'save',r['ok'],r.get('error'))
    cli('editor.cancel',{'id':op}); time.sleep(2)
