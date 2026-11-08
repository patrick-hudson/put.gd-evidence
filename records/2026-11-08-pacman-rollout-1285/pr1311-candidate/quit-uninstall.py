import sys,pathlib
sys.path.insert(0,str(pathlib.Path.home()/'work/r1285/tools/lab'));import lab
run=pathlib.Path.home()/'work/r1285/work/lab-runs/o3'
body='''set -eu
export XDG_RUNTIME_DIR=/tmp/p1285/r XDG_CONFIG_HOME=/tmp/p1285/c XDG_DATA_HOME=/tmp/p1285/d XDG_STATE_HOME=/tmp/p1285/s XDG_CACHE_HOME=/tmp/p1285/cache
/usr/bin/putgd-cli ui.quit
sleep 1
test ! -S /tmp/p1285/r/putgd/session.sock
! pgrep -x putgd
sudo -n pacman -R --noconfirm putgd
! pacman -Q putgd
test ! -e /usr/bin/putgd
test ! -e /usr/bin/putgd-cli
test -r /etc/pacman.d/putgd.conf
printf 'PASS native quit, uninstall and retained readable repository config\\n'
'''
print(lab.guest_session(run,body,timeout=60));print(lab.screenshot(run,'after-uninstall'))
