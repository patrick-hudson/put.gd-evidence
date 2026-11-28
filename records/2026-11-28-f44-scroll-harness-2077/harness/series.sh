#!/bin/bash
# #2077 proof on f44: the fixed sess.py/live7.py with Firefox on GitHub, the
# Python docs and Wikipedia (control), user and auto, against the published
# nightly 26.1126.7275 installed as a user would. Run under desktop_lock.py run.
set -u
cd ~/work/h2077 || exit 1
echo "start $(date -u +%FT%TZ)"
gnome-extensions list --enabled | grep -qx putgd@put.gd || { echo "putgd extension off"; exit 1; }
gnome-extensions list --enabled | grep -qx appindicatorsupport@rgcjonas.gmail.com || { echo "tray off"; exit 1; }
RPM=putgd-26.1126.7275-nightly-fedora44-x86_64.rpm
if [ "$(rpm -q putgd)" != "putgd-26.1126.7275~nightly-1.fc44.x86_64" ]; then
  test -s pkg/$RPM || curl -fsSL -o pkg/$RPM https://github.com/patrick-hudson/put.gd-desktop/releases/download/v26.1126.7275-nightly/$RPM || exit 1
  sudo -n dnf install -y ./pkg/$RPM > pkg/install.log 2>&1; echo "dnf install exit $?"
fi
rpm -q putgd
INFO=$(rpm -ql putgd | grep "build-info.json$" | head -1)
cmp "$INFO" src/build/release/build-identity/build-info.json && echo "driver identity = package identity ($INFO)" || { echo "identity mismatch"; exit 1; }
test -z "$(pgrep -x putgd-record || true)" || { echo "helper running"; exit 1; }
sudo -n setfacl -m u:patrick:rw /dev/uinput
export LAB_X11=0 SF7_VNC=5901 PYTHONHASHSEED=0 PYTHONDONTWRITEBYTECODE=1 XDG_RUNTIME_DIR=/run/user/$(id -u)
export LAB_BUILD_DIR=$HOME/work/h2077/src/build/release LAB_HELPER=/usr/bin/putgd-record LAB_DIR=$HOME/work/h2077/lab/lane LAB_TAG=n7275
mkdir -p $LAB_DIR/t $LAB_DIR/c $LAB_DIR/k $LAB_DIR/s
ln -sfn $HOME/work/h2077/lab/tools $LAB_DIR/tools; cp lab/umouse.py $LAB_DIR/
cd lab
TMPDIR=$LAB_DIR/t XDG_CONFIG_HOME=$LAB_DIR/c XDG_CACHE_HOME=$LAB_DIR/k XDG_STATE_HOME=$LAB_DIR/s python3 -u sess.py firefox github,python,wiki user,auto
echo "sess exit $?"
sudo -n setfacl -x u:patrick /dev/uinput
test -z "$(pgrep -x putgd-record || true)" && echo "no helper left"
echo "end $(date -u +%FT%TZ)"
