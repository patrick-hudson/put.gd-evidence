# acc.py <guest key> <suffix> <mode> [n]: fix round 3 acceptance cases in one lab guest (after v3host.py).
import sys,json,time,shlex,traceback
from pathlib import Path
from PIL import Image
B=Path("/home/patrick/work/svm1398");sys.path.insert(0,str(B/"repo/tools/lab"));import lab
k,suffix,mode=sys.argv[1:4];count=int(sys.argv[4]) if len(sys.argv)>4 else 5
r=B/"repo/work/lab-runs"/(k+suffix);o=Path("/home/patrick/work/scn/ev")/(k+suffix);o.mkdir(parents=True,exist_ok=True)
def cmd(c,timeout=300):return lab.guest_session(r,c,timeout=timeout)
def shot(n):Image.open(lab.screenshot(r,"sf3-"+n)["path"]).save(o/(n+".png"))
def spawn(c,n):return int(cmd("nohup "+c+" > /tmp/v3/"+n+".log 2>&1 < /dev/null & echo $!").strip())
def case(n,rect="0,0,1280,800",before=False):
    if before:shot(n+"-before")
    print(k,n,"START",time.strftime("%H:%M:%S"),flush=True);(o/(n+".console")).write_text(cmd("python3 /home/lab/v3guest.py case "+n+" "+rect));shot(n+"-end");print(k,n,"END",time.strftime("%H:%M:%S"),flush=True)
def fixture(args,name):
    pid=spawn("env SC_Y=100 python3 /home/lab/v3ruler.py "+args,name);time.sleep(3);return pid
try:
    if mode=="native":
        pid=fixture("","native")
        for i in range(1,count+1):case("native%02d"%i,"100,100,960,600")
        cmd("kill "+str(pid))
    elif mode in ["rapid","burst"]:
        # A browser page, the whole screen; each capture begins as soon as the one before has uploaded and shown its toast.
        browser="chromium --no-first-run --password-store=basic --user-data-dir=/tmp/v3/chromium --kiosk file:///home/lab/v3ruler.html" if k=="o" else "firefox --no-remote --profile /home/lab/v3firefox --kiosk file:///home/lab/v3ruler.html"
        if k!="o":
            cmd("mkdir -p /home/lab/v3firefox");prefs="user_pref(\"browser.shell.checkDefaultBrowser\", false); user_pref(\"browser.aboutwelcome.enabled\", false); user_pref(\"browser.startup.homepage_override.mstone\", \"ignore\");"
            cmd("printf %s "+shlex.quote(prefs)+" > /home/lab/v3firefox/user.js")
        pid=spawn(browser,"browser");time.sleep(18);shot("browser-ready")
        for i in range(1,(count+1 if mode=="burst" else count+4)):case(("burst%02d"%i) if mode=="burst" else ("rapid%02d"%i) if i<=count else ("burst%02d"%(i-count)),before=True)
        cmd("kill "+str(pid)+" || true");time.sleep(2)
    elif mode=="text":
        for kind in ["qt","gtk"]:
            for width in [1280,600]:
                name=kind+str(width);pid=spawn("python3 /home/lab/v3text.py "+kind+" "+str(width),name);time.sleep(4);shot(name+"-ready")
                for i in range(1,count+1):case(name+"-"+str(i),"0,100,"+str(width-20)+",600")
                cmd("kill "+str(pid));time.sleep(1)
    elif mode=="capflow":
        # The height cap and its warning, then the next capture at once.
        pid=fixture("--rows 600","capflow");case("cap","100,100,960,600");case("postcap","100,100,960,600",before=True);cmd("kill "+str(pid));time.sleep(1)
    elif mode=="stoptop":
        for i in range(1,count+1):
            pid=fixture("--rows 600 --start 12000","stop-top-%d"%i);case("stop-top-%d"%i,"100,100,960,600");cmd("kill "+str(pid));time.sleep(1)
    elif mode=="extras":
        for name,start in [("long1",0),("half-on",12000),("half-off",12000),("stop-mid",0),("cancel",0)]:
            pid=fixture("--rows 600 --start "+str(start),name);case(name,"100,100,960,600");cmd("kill "+str(pid));time.sleep(1)
    elif mode=="export":
        code="""import tarfile,json,hashlib
from pathlib import Path
p=Path("/tmp/v3");files=[]
for n in ["cases"]:
    files += [f for f in (p/n).rglob("*") if f.is_file()]
files += [f for f in p.iterdir() if f.is_file() and (f.suffix in [".log",".json",".jsonl"])]
with tarfile.open("/home/lab/sf3-export.tgz","w:gz") as t:
    for f in files:t.add(f,arcname=str(f.relative_to(p)))
print(json.dumps({str(f.relative_to(p)):hashlib.sha256(f.read_bytes()).hexdigest() for f in files}))
"""
        (o/"hashes.json").write_text(cmd("python3 -c "+shlex.quote(code)));lab.get(r,"/home/lab/sf3-export.tgz",o/"export.tgz");import tarfile
        (o/"final").mkdir(exist_ok=True);tarfile.open(o/"export.tgz").extractall(o/"final",filter="data");print(k,"EXPORTED",flush=True)
    print(k,mode,"DONE",flush=True)
except Exception:
    (o/(mode+"-error.txt")).write_text(traceback.format_exc());print(k,traceback.format_exc(),flush=True);sys.exit(1)
