import sys,time,json,subprocess,concurrent.futures,traceback
from pathlib import Path
from PIL import Image
sys.path.insert(0,'/home/patrick/work/svm1398/repo/tools/lab');import lab
base=Path('/home/patrick/work/svm1398')
def run(k):
 r=base/'repo/work/lab-runs'/(k+'f');o=base/'v2evidence'/k
 def cmd(c):return lab.guest_session(r,c,timeout=300)
 def shot(n):Image.open(lab.screenshot(r,'v2-'+n)['path']).save(o/(n+'.png'))
 if sys.argv[1]=='launch':
  old=o/'harness-welcome-witnesses';old.mkdir(exist_ok=True)
  for f in list(o.iterdir()):
   if f.is_file() and f.suffix in ['.png','.console']:__import__('shutil').copy2(f,old/f.name)
  pid=cmd('nohup firefox --no-remote --profile /tmp/v2/firefox --kiosk file:///home/lab/v2ruler.html > /tmp/v2/browser-retry.log 2>&1 < /dev/null & echo $!').strip();(o/'browser-retry.pid').write_text(pid);time.sleep(15);shot('browser-retry-ready');return
 for name in ['plain-r1','plain-r2','plain-r3','cap','postcap','stop']:
  # Preserve invalid welcome-dialog attempts at original paths.
  cmd("python3 -c "+__import__('shlex').quote("from pathlib import Path;p=Path('/tmp/v2/cases/"+name+"');p.rename(p.with_name('harness-welcome-"+name+"')) if p.exists() else None"))
  print(k,name,'START',flush=True);(o/(name+'.console')).write_text(cmd('python3 /home/lab/v2guest.py case '+name+' 0,0,1280,800'));time.sleep(1);shot(name+'-end');print(k,name,'END',flush=True)
 env=dict(__import__('os').environ,VM_RUN=k)
 subprocess.run([str(base/'repo/tools/mcp/.venv/bin/python'),str(base/'v2mcp.py'),k],env=env,stdout=(o/'mcp-retry.console').open('w'),stderr=subprocess.STDOUT,timeout=300)
 cmd('kill '+(o/'browser-retry.pid').read_text())
with concurrent.futures.ThreadPoolExecutor(4) as pool:list(pool.map(run,sys.argv[2]))
