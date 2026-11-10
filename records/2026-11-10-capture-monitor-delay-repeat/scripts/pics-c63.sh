#!/bin/sh
# pics-c63.sh: on the two-head Cinnamon guest c63 (run on m74): a delayed capture that keeps an open
# menu with its hovered row, and a two-monitor desk beside the single-monitor capture.
D=/tmp/p1363-vmdrive.py; R=c63; K=$HOME/work/put.gd/work/lab-bootstrap-m74/identity; cd $HOME/work/i1363; mkdir -p /tmp/p1363-pics
port=$(python3 -c "import json; print(json.load(open('$HOME/work/i1363/work/lab-runs/$R/state.json'))['ssh_port'])")
key() { python3 tools/lab/lab.py key --run work/lab-runs/$R "$1" >/dev/null; }
newest() { f=$(/tmp/p1363-gs.sh $R $K "ls -t ~/Documents/put.gd/images/*.png | head -1"); scp -q -i $K -P $port -o IdentitiesOnly=yes -o BatchMode=yes -o StrictHostKeyChecking=yes -o UserKnownHostsFile=$HOME/work/i1363/work/hostkeys/$R/known_hosts "lab@127.0.0.1:$f" "$1" < /dev/null; }
# A file manager window on head 1 (the smaller monitor), placed there whatever was open before.
/tmp/p1363-gs.sh $R $K 'export DISPLAY=:0 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$(id -u)/bus; xwininfo -root -tree 2>/dev/null | grep -q "\"backgrounds\"" || { setsid -f nemo /usr/share/backgrounds > /dev/null 2>&1 < /dev/null; sleep 4; }; wmctrl -r backgrounds -e 0,1330,82,800,550; sleep 1; wmctrl -a backgrounds; sleep 1; xwininfo -root -tree | grep "\"backgrounds\"" | head -1'
python3 $D $R click 0 1238 35 >/dev/null; sleep 0.5; python3 $D $R click 0 1238 35 >/dev/null; sleep 0.5
# The context menu of the file area, pointer resting on one of its rows.
python3 $D $R click 1 520 420 right >/dev/null; sleep 1.2; python3 $D $R move 1 590 480 >/dev/null; sleep 0.3; python3 $D $R move 1 600 496 >/dev/null; sleep 1
/tmp/p1363-shot.sh $R 0 desk-head0 >/dev/null; /tmp/p1363-shot.sh $R 1 desk-head1 >/dev/null
id=$(python3 $D $R start monitor 5); sleep 2.2; /tmp/p1363-shot.sh $R 1 hover-during >/dev/null; python3 $D $R wait $id | cut -c1-90
newest /tmp/p1363-pics/raw-cinnamon-hover-capture.png
for n in desk-head0 desk-head1 hover-during; do cp /tmp/p1363-shots/$R-$n.png /tmp/p1363-pics/raw-cinnamon-$n.png; done
key esc
