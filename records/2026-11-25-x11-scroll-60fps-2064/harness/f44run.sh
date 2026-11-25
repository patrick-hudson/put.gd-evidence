set -u
cd ~/work/x2064/f44lab || exit 1
gnome-extensions list --enabled | grep -qx putgd@put.gd || { echo "putgd extension off"; exit 1; }
gnome-extensions list --enabled | grep -qx appindicatorsupport@rgcjonas.gmail.com || { echo "tray off"; exit 1; }
test -z "$(pgrep -x putgd-record || true)" || { echo "helper running"; exit 1; }
sudo -n setfacl -m u:patrick:rw /dev/uinput
export LAB_X11=0 SF7_VNC=5901 PYTHONHASHSEED=0 PYTHONDONTWRITEBYTECODE=1 XDG_RUNTIME_DIR=/run/user/$(id -u)
for b in nightly cand1; do
  export LAB_BUILD_DIR=$HOME/work/x2064/$b/src/build/release
  if [ $b = nightly ]; then export LAB_HELPER=/usr/bin/putgd-record; else export LAB_HELPER=$HOME/work/x2064/cand1/pkg/usr/bin/putgd-record; fi
  export LAB_DIR=$HOME/work/x2064/f44lab/lane-$b
  mkdir -p $LAB_DIR/t $LAB_DIR/c $LAB_DIR/k $LAB_DIR/s; ln -sfn $HOME/work/x2064/f44lab/tools $LAB_DIR/tools; cp umouse.py $LAB_DIR/
  TMPDIR=$LAB_DIR/t XDG_CONFIG_HOME=$LAB_DIR/c XDG_CACHE_HOME=$LAB_DIR/k XDG_STATE_HOME=$LAB_DIR/s LAB_TAG=$b python3 -u sess.py firefox wiki,github user,auto
done
sudo -n setfacl -x u:patrick /dev/uinput
getfacl /dev/uinput 2>/dev/null | grep -c "user:patrick" 
test -z "$(pgrep -x putgd-record || true)" && echo "no helper left"
