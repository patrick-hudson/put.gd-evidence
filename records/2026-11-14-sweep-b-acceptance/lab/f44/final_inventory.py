import os,json,pathlib,subprocess,socket,datetime
root=pathlib.Path('/home/patrick/work/sb1114')
def run(args):
 p=subprocess.run(args,text=True,capture_output=True);return {'exitCode':p.returncode,'stdout':p.stdout.strip()}
def size(p):
 v=run(['du','-sb',str(p)]);return int(v['stdout'].split()[0]) if v['exitCode']==0 else None
paths=[root,root.with_name('sb1114-source.tar')]
for pattern in ('sbm[0-9]*','sba[12]','sbk[12]'):
 paths.extend(pathlib.Path('/tmp').glob(pattern))
for p in root.glob('physical-*.log'):
 for line in p.read_text(errors='replace').splitlines()[:4]:
  try:
   v=json.loads(line).get('socketPath','')
   if v.startswith('/tmp/sbr') and v.endswith('/putgd/session.sock'):paths.append(pathlib.Path(v).parents[1])
  except (ValueError,AttributeError):pass
owned=[]
for p in pathlib.Path('/proc').iterdir():
 if not p.name.isdecimal():continue
 try:
  args=(p/'cmdline').read_bytes().split(b'\0');env=(p/'environ').read_bytes().split(b'\0')
  belongs=any(str(root).encode() in x for x in args) or any(x.startswith((b'XDG_CONFIG_HOME=/tmp/sbm',b'XDG_CONFIG_HOME=/tmp/sba',b'XDG_CONFIG_HOME=/tmp/sbk')) for x in env)
  if belongs and int(p.name)!=os.getpid():owned.append({'pid':int(p.name),'comm':(p/'comm').read_text().strip(),'executable':os.readlink(p/'exe')})
 except (OSError,PermissionError):pass
package=run(['dpkg-query','-W','-f=${Status} ${Version}\n','putgd']) if pathlib.Path('/usr/bin/dpkg-query').exists() else run(['rpm','-q','putgd'])
print(json.dumps({'host':socket.gethostname(),'timestampUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'package':package,'scratch':[{'path':str(p),'bytes':size(p)} for p in sorted(set(paths)) if p.exists()],'ownedProcesses':owned,'gnomeExtension':'untouched by round B'},indent=2))
