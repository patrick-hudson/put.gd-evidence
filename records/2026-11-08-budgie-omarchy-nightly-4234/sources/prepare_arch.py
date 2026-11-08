import sys,json,shutil
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
from tools.lab import lab,nightly_desktop_guest as g
r=Path(sys.argv[1]).resolve();out=Path(sys.argv[2]).resolve();out.mkdir(mode=0o700,parents=True,exist_ok=False)
protected='hyprland omarchy quickshell xdg-desktop-portal xdg-desktop-portal-hyprland pipewire mesa'
before=lab.ssh(r,'pacman -Q '+protected);(out/'desktop-before.txt').write_text(before)
packages='python-pyqt6 python-atspi python-dbus python-pillow python-gobject tesseract tesseract-data-eng xdotool xorg-xprop xorg-xwininfo xorg-xrandr xclip wl-clipboard gst-plugin-gtk gnome-keyring qtkeychain-qt6'
install=lab.ssh(r,'sudo -n pacman -Sy --needed --noconfirm --ignore hyprland,omarchy,quickshell,xdg-desktop-portal,xdg-desktop-portal-hyprland,pipewire,mesa '+packages,timeout=900)
(out/'probe-install.txt').write_text(install)
after=lab.ssh(r,'pacman -Q '+protected);(out/'desktop-after.txt').write_text(after);assert before==after
(out/'nag-suppression.json').write_text(lab.guest_session(r,g.QUIET,timeout=60))
(out/'ram-placement.json').write_text(lab.guest_session(r,g.RAM))
from tools.lab.stage_firefox import stage
browser=json.loads(stage(r));(out/'firefox.json').write_text(json.dumps(browser,indent=2))
profiles=out/'profiles';shutil.copytree(Path('tools/lab/surface_driver/profiles'),profiles)
fragment=profiles/'omarchy-hyprland.d/zz-private.json';fragment.parent.mkdir(parents=True,exist_ok=True)
fragment.write_text(json.dumps({'browser':dict(command=browser['command'],profile_root='/dev/shm/nd-firefox')}))
print(profiles)
