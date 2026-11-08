import sys,json,fnmatch
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
from tools.lab import lab,nightly_desktop_guest as g
r=Path(sys.argv[1]).resolve();out=Path(sys.argv[2]).resolve();desktop=sys.argv[3];package=sys.argv[4];out.mkdir(mode=0o700,parents=True,exist_ok=False)
patterns=('labwc*','budgie*','gnome-shell*','mutter*','xdg-desktop-portal*','pipewire*','kernel*')
def inventory():
 raw=lab.ssh(r,"rpm -qa --qf '%{NAME} %{EPOCHNUM}:%{VERSION}-%{RELEASE}\\n'")
 return sorted(l for l in raw.splitlines() if any(fnmatch.fnmatchcase(l.split()[0],p) for p in patterns))
before=inventory();(out/'desktop-before.json').write_text(json.dumps(before))
(out/'probe-install.txt').write_text(lab.ssh(r,'sudo -n dnf --color=never --exclude='+','.join(patterns)+' install -y '+g.FEDORA_TOOLS,timeout=900))
after=inventory();(out/'desktop-after.json').write_text(json.dumps(after));assert before==after
print(g.prepare(r,dict(desktop=desktop,package=package,probePackageManager='rpm'),out))
