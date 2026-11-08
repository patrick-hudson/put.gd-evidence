import sys,json
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
from tools.lab import lab
run,out=sys.argv[1:];run=Path(run).resolve()
code=r'''import subprocess,time,json,os,signal
payload=b'putgd synthetic ordinary wl-copy lifetime control'
p=subprocess.Popen(['wl-copy','--foreground','--type','text/plain'],stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True)
p.stdin.write(payload);p.stdin.close();time.sleep(1)
def read():
 try:
  r=subprocess.run(['wl-paste','--no-newline','--type','text'],capture_output=True,timeout=3);return r.stdout==payload
 except subprocess.TimeoutExpired:return False
before=read();p.terminate();p.wait(timeout=5);time.sleep(2);after=read()
processes=subprocess.run(['ps','-u',str(os.getuid()),'-o','comm='],capture_output=True,text=True).stdout.splitlines()
print(json.dumps(dict(before=before,afterOwnerExit=after,plainWlCopyControl=True,clipboardManagers=[p.strip() for p in processes if any(n in p for n in ('clip','copyq','gpaste','quickshell','budgie'))])))
'''
raw=lab.guest_session(run,"python3 - <<'BASELINE'\n"+code+'\nBASELINE\n');Path(out).write_text(raw);print(raw)
