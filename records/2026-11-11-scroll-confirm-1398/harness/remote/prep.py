# prep.py <key> <suffix> deps|install [appimage]: guest dependencies (detached, with a done marker) or the CI AppImage and the isolated resident
import sys,json,time
from pathlib import Path
from PIL import Image
B=Path("/home/patrick/work/svm1398");sys.path.insert(0,str(B/"repo/tools/lab"));import lab
k,suffix,mode=sys.argv[1:4];r=B/"repo/work/lab-runs"/(k+suffix);o=Path("/home/patrick/work/scn/ev")/(k+suffix);o.mkdir(parents=True,exist_ok=True)
def cmd(c,timeout=300):return lab.guest_session(r,c,timeout=timeout)
deps={"o":"pacman -Sy --noconfirm python-gobject gtk4 python-pyqt6 python-pillow python-numpy","b":"dnf --setopt=zchunk=False --setopt=timeout=20 install -y python3-gobject gtk4 python3-pyqt6-base python3-pillow python3-numpy" ,"n":"apt-get update && sudo -n apt-get install -y python3-gi gir1.2-gtk-4.0 python3-pyqt6 python3-pil python3-numpy","k":"apt-get update && sudo -n apt-get install -y python3-gi gir1.2-gtk-4.0 python3-pyqt6 python3-pil python3-numpy"}[k]
if mode=="deps":
    print(lab.ssh(r,"nohup sh -c "+repr("sudo -n "+deps+" > /tmp/deps.log 2>&1; echo $? > /tmp/deps.done")+" > /dev/null 2>&1 < /dev/null & echo started",timeout=60))
elif mode=="depsdone":
    print(lab.ssh(r,"cat /tmp/deps.done 2>/dev/null || echo running; tail -c 200 /tmp/deps.log",timeout=60))
elif mode=="install":
    (o/"install.json").write_text(json.dumps(lab.install(r,appimage=Path(sys.argv[4])),indent=2))
    for source,target in [(Path("/home/patrick/work/scn/v3guest.py"),"v3guest.py"),(Path("/home/patrick/work/scn/f4text.py"),"v3text.py"),(B/"v3receiver.py","v3receiver.py"),(Path("/home/patrick/work/scn/ruler.html"),"v3ruler.html"),(Path("/home/patrick/work/sf1398/qt_fixture.py"),"v3ruler.py"),(B/"repo/tools/lab/wayland_pointer.py","wayland_pointer.py"),(B/"repo/tools/lab/wayland_toplevels.py","wayland_toplevels.py")]:
        lab.put(r,source,"/home/lab/"+target)
    (o/"init.log").write_text(cmd("python3 /home/lab/v3guest.py init"))
    (o/"identity.log").write_text(cmd("cat /etc/os-release; loginctl list-sessions; (kwin_wayland --version || labwc --version || hyprctl version) 2>/dev/null; cat /tmp/v3/version.json"))
    Image.open(lab.screenshot(r,"sf3-desktop-ready")["path"]).save(o/"desktop-ready.png");print(k,"PREPARED",flush=True)
