#!/bin/sh
# pics-kde-150.sh: the put.gd window at 150% on the KDE guest k63 (run on k72): head 0 becomes 1920x1200 at scale 1.5.
D=/tmp/p1363-vmdrive.py; R=k64; K=$HOME/work/put.gd/work/lab-bootstrap-k72/identity; cd $HOME/work/i1363; mkdir -p /tmp/p1363-pics
E='export XDG_RUNTIME_DIR=/run/user/$(id -u) WAYLAND_DISPLAY=wayland-0;'
/tmp/p1363-gs.sh $R $K "$E kscreen-doctor output.Virtual-1.mode.1920x1200@60 output.Virtual-1.scale.1.5; sleep 3; kscreen-doctor -o | sed 's/\x1b\[[0-9;]*m//g' | grep -E 'Geometry|Scale'"
python3 $D $R gmove 600 400 >/dev/null; python3 $D $R cli ui.show '{"view":"activity"}' >/dev/null; sleep 3
# The window is on head 1 from the earlier pictures: KWin's "Window to Previous Screen" (Meta+Shift+Left) brings it over.
python3 tools/lab/lab.py key --run work/lab-runs/$R meta_l shift left >/dev/null; sleep 3
/tmp/p1363-shot.sh $R 0 dash150 >/dev/null; cp /tmp/p1363-shots/$R-dash150.png /tmp/p1363-pics/raw-kde-dash150.png
python3 tools/lab/lab.py key --run work/lab-runs/$R meta_l shift right >/dev/null; sleep 2
/tmp/p1363-gs.sh $R $K "$E kscreen-doctor output.Virtual-1.scale.1 output.Virtual-1.mode.1280x800@75; sleep 3; kscreen-doctor output.Virtual-2.position.1280,0; sleep 1; kscreen-doctor -o | sed 's/\x1b\[[0-9;]*m//g' | grep -E 'Geometry|Scale'"
