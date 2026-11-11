import sys,json,time,subprocess,shlex,concurrent.futures,traceback
from pathlib import Path
sys.path.insert(0,'/home/patrick/work/svm1398/repo/tools/lab');import lab
base=Path('/home/patrick/work/svm1398');ev=base/'v2evidence';ev.mkdir(exist_ok=True)
def run(k):
 r=base/'repo/work/lab-runs'/(k+'f');o=ev/k;o.mkdir(exist_ok=True)
 def cmd(c):return lab.guest_session(r,c,timeout=300)
 def shot(n):
  f=lab.screenshot(r,'v2-'+n);__import__('PIL.Image',fromlist=['Image']).open(f["path"]).save(o/(n+'.png'))
 def case(n,rect):
  print(k,n,'START',flush=True)
  (o/(n+'.console')).write_text(cmd('python3 /home/lab/v2guest.py case '+n+' '+rect))
  shot(n+'-end')
  print(k,n,'END',flush=True)
 def fixture(kind):
  c='python3 /home/lab/v2text.py '+kind
  pid=int(cmd('nohup '+c+' > /tmp/v2/'+kind+'.log 2>&1 < /dev/null & echo $!').strip())
  time.sleep(4);shot(kind+'-ready');return pid
 try:
  for kind in ['gtk','qt']:
   pid=fixture(kind)
   try:
    for i in range(1,4):case(kind+str(i),'100,100,940,600')
   finally:cmd('kill '+str(pid));time.sleep(1)
  # Browser starts after app installation and fixture checks; wait for real paint.
  browser='chromium --no-first-run --password-store=basic --user-data-dir=/tmp/v2/chromium --kiosk file:///home/lab/v2ruler.html' if k=='o' else 'firefox --no-remote --profile /tmp/v2/firefox --kiosk file:///home/lab/v2ruler.html'
  cmd('mkdir -p /tmp/v2/firefox')
  pid=int(cmd('nohup '+browser+' > /tmp/v2/browser.log 2>&1 < /dev/null & echo $!').strip());time.sleep(16);shot('browser-ready')
  for i in range(1,4):case('plain'+str(i),'0,0,1280,800')
  case('cap','0,0,1280,800');case('postcap','0,0,1280,800');case('stop','0,0,1280,800')
  env=dict(__import__('os').environ,VM_RUN=k)
  subprocess.run([str(base/'repo/tools/mcp/.venv/bin/python'),str(base/'v2mcp.py'),k],env=env,stdout=(o/'mcp.console').open('w'),stderr=subprocess.STDOUT,timeout=300)
  cmd('kill '+str(pid))
 except Exception as e:
  (o/'harness-error.txt').write_text(traceback.format_exc());print(k,'ERROR',e,flush=True)
 finally:
  # Explicit evidence allowlist; never copy profile environment, keys or browser profile.
  script="""python3 - <<'INNER'
import tarfile,hashlib,json
from pathlib import Path
p=Path('/tmp/v2');files=[]
for name in ['cases','archive','received']:
 files += [f for f in (p/name).rglob('*') if f.is_file()]
for name in ['helper.log','resident.log','rpc.jsonl','version.json','capabilities.json','socket-preflight.json','gtk.log','qt.log','browser.log']:
 if (p/name).is_file():files.append(p/name)
with tarfile.open('/home/lab/v2-export.tgz','w:gz') as t:
 for f in files:t.add(f,arcname=str(f.relative_to(p)))
print(json.dumps({str(f.relative_to(p)):hashlib.sha256(f.read_bytes()).hexdigest() for f in files}))
INNER"""
  try:
   (o/'export-hashes.json').write_text(cmd(script));lab.get(r,'/home/lab/v2-export.tgz',o/'export.tgz',timeout=180)
  except Exception:(o/'export-error.txt').write_text(traceback.format_exc())
with concurrent.futures.ThreadPoolExecutor(4) as pool:list(pool.map(run,'obnk'))
