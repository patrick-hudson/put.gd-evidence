from control import *
def f(h):
 script='''import pathlib,json,hashlib,subprocess,os
p=pathlib.Path.home()/'c1245b'
b=json.loads((p/'packages/build-info.json').read_text());c=json.loads((p/'catalog/manifest.json').read_text())
assert b['gitCommit']==c['build']['gitCommit']=='05b61eec291e510ae6b7e67855345dd9e3816963'
files=[f for f in (p/'packages').iterdir() if f.suffix in ('.deb','.rpm','.AppImage')]
assert len(files)==1
h=HOST
asset=ASSET
identity=dict(gitCommit=b['gitCommit'],driver=subprocess.check_output(['git','-C',str(pathlib.Path.home()/'nd'),'rev-parse','HEAD'],text=True).strip(),packages={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in files},packageFiles={asset:files[0].name},ciRun=42363534641,prHead='ec3b48c777d116a0fe41d9cf4bd44b54cbf91ca9')
(p/'identity.json').write_text(json.dumps(identity,indent=2))
log=(p/'worker.log').open('x')
proc=subprocess.Popen(['python3',str(pathlib.Path.home()/'nd/tools/lab/nightly_desktops.py'),'--worker',h,'--artifacts',str(p),'--output',str(p/'out'),'v26.1107.4026-dev+g05b61eec291e'],stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
(p/'worker.pid').write_text(str(proc.pid))
print(json.dumps(identity));print('worker',proc.pid)
'''.replace('HOST',repr(h)).replace('ASSET',repr({'m74':'ubuntu24.04-x86_64.deb','d69':'ubuntu26.04-x86_64.deb','k72':'ubuntu26.04-x86_64.deb','f44':'fedora44-x86_64.rpm','aurora-amd':'x86_64.AppImage'}[h]))
 r=ssh(h,'cd ~/nd && python3 -c '+shlex.quote(script),timeout=30);return h,r.returncode,r.stdout,r.stderr
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
 for r in ex.map(f,hosts):print(r,flush=True)
