import sys,json,fnmatch
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
from tools.lab import lab
run,kind,out=sys.argv[1:];run=Path(run).resolve();out=Path(out);out.mkdir(mode=0o700)
if kind=='arch':
 protected='hyprland omarchy quickshell xdg-desktop-portal xdg-desktop-portal-hyprland pipewire mesa'
 before=lab.ssh(run,'pacman -Q '+protected)
 log=lab.ssh(run,'sudo -n pacman -S --needed --noconfirm --ignore '+protected.replace(' ', ',')+' wl-clip-persist',timeout=300)
 after=lab.ssh(run,'pacman -Q '+protected);helptext=lab.ssh(run,'wl-clip-persist --help')
else:
 before=lab.ssh(run,"rpm -qa --qf '%{NAME} %{VERSION}-%{RELEASE}\\n'" if kind=='rpm' else "dpkg-query -W -f='${binary:Package} ${Version}\\n'")
 protected=('labwc*','budgie*','gnome-shell*','mutter*','pipewire*','xdg-desktop-portal*','mesa*')
 before='\n'.join(sorted(l for l in before.splitlines() if any(fnmatch.fnmatchcase(l.split()[0],p) for p in protected)))
 command='sudo -n dnf --color=never --exclude='+','.join(protected)+' install -y clipman' if kind=='rpm' else 'sudo -n apt-get install -y --no-install-recommends clipman'
 log=lab.ssh(run,command,timeout=300)
 after=lab.ssh(run,"rpm -qa --qf '%{NAME} %{VERSION}-%{RELEASE}\\n'" if kind=='rpm' else "dpkg-query -W -f='${binary:Package} ${Version}\\n'")
 after='\n'.join(sorted(l for l in after.splitlines() if any(fnmatch.fnmatchcase(l.split()[0],p) for p in protected)))
 helptext=lab.ssh(run,'clipman store --help')
assert before==after
(out/'before.txt').write_text(before);(out/'after.txt').write_text(after);(out/'install.txt').write_text(log);(out/'help.txt').write_text(helptext);print(helptext)
