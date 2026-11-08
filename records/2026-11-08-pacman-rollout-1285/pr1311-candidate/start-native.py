import sys,pathlib,json
sys.path.insert(0,str(pathlib.Path.home()/'work/r1285/tools/lab'))
import lab
run=pathlib.Path.home()/'work/r1285/work/lab-runs/o3'
body='''set -eu
case "$WAYLAND_DISPLAY" in /*) ;; *) export WAYLAND_DISPLAY=/run/user/$(id -u)/$WAYLAND_DISPLAY ;; esac
umask 077
mkdir -p /tmp/p1285/r /tmp/p1285/c /tmp/p1285/d /tmp/p1285/s /tmp/p1285/cache
export XDG_RUNTIME_DIR=/tmp/p1285/r XDG_CONFIG_HOME=/tmp/p1285/c XDG_DATA_HOME=/tmp/p1285/d XDG_STATE_HOME=/tmp/p1285/s XDG_CACHE_HOME=/tmp/p1285/cache
/usr/bin/putgd-cli --version
pacman -Qkk putgd
cat /etc/pacman.d/putgd.conf
pacman -Q hyprland
/usr/bin/putgd-cli capabilities
/usr/bin/putgd-cli diagnostics
'''
r=lab.guest_session(run,body,timeout=60)
print(r)
print(lab.screenshot(run,'native-startup'))
