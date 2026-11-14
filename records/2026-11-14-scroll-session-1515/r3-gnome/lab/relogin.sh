#!/bin/bash
# relogin.sh VERSION : install put.gd's Shell extension at VERSION (23 or 24) for this user, log in again, leave the overview.
set -u
lab=$HOME/work/scroll-session/gnome
ext=$HOME/.local/share/gnome-shell/extensions/putgd@put.gd
mkdir -p "$ext"
cp "$lab/ext-v$1/extension.js" "$lab/ext-v$1/metadata.json" "$ext/"
sudo -n systemctl restart gdm
for i in $(seq 1 60); do sleep 2; systemctl --user show-environment 2>/dev/null | grep -q '^WAYLAND_DISPLAY=' && gnome-extensions info putgd@put.gd 2>/dev/null | grep -q 'State: ACTIVE' && break; done
sleep 4
systemctl --user restart putgd-gnome-vnc
sleep 4
bash "$lab/envgen.sh" > /dev/null
python3 - <<PY
import sys, time
sys.path.insert(0, "$lab")
import rfb
v = rfb.RFB(5901)
v.key('esc')
time.sleep(0.5)
v.close()
PY
gnome-extensions info putgd@put.gd | grep -E "Version|State"
