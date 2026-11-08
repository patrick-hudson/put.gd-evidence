python3 - <<'PY'
from pathlib import Path
import os,signal,time
pid=int(Path('/tmp/magpie-a2/pid').read_text());cmd=Path('/proc')/str(pid)/'cmdline';assert cmd.read_bytes().split(b'\0')[0]==b'/home/lab/magpie-probe'
os.kill(pid,signal.SIGTERM);time.sleep(2)
out=Path('/tmp/magpie-seat');out.mkdir(mode=0o700)
script=Path.home()/'magpie-session.sh'
script.write_text('''#!/bin/sh
unset DISPLAY WAYLAND_DISPLAY
export QT_QPA_PLATFORM=offscreen
exec /home/lab/magpie-probe --console-provider logind --input-report log --app '/usr/bin/foot -a a1275-magpie-seat -T A1275-Magpie-direct-seat -e /usr/bin/tee /tmp/magpie-seat-physical-input' > /tmp/magpie-seat/compositor.log 2>&1
''');script.chmod(0o700)
root=Path.home()/'magpie-root-setup.sh'
root.write_text('''#!/bin/sh
set -eu
test ! -e /usr/share/wayland-sessions/a1275-magpie.desktop
test ! -e /etc/sddm.conf.d/99-z-a1275-magpie.conf
cat > /usr/share/wayland-sessions/a1275-magpie.desktop <<'D'
[Desktop Entry]
Name=A1275 Magpie compositor probe
Exec=/home/lab/magpie-session.sh
Type=Application
DesktopNames=Magpie-probe
D
cat > /etc/sddm.conf.d/99-z-a1275-magpie.conf <<'D'
[Autologin]
User=lab
Session=a1275-magpie.desktop
Relogin=true
D
systemctl restart sddm
''');root.chmod(0o700)
print('prepared direct-seat entry; only owned disposable overlay')
PY
