#!/bin/sh
# pics-c62.sh: the put.gd-drawn "after" pictures on the one-head Cinnamon guest c62 (run on m74).
D=/tmp/p1363-vmdrive.py; R=c62; cd $HOME/work/i1363
key() { python3 tools/lab/lab.py key --run work/lab-runs/$R "$1" >/dev/null; }
shot() { /tmp/p1363-shot.sh $R 0 "$1" >/dev/null; cp /tmp/p1363-shots/$R-$1.png /tmp/p1363-pics/raw-cinnamon-$1.png; }
mkdir -p /tmp/p1363-pics
# The before pictures were taken on a fresh configuration (no output yet), so the first four match it.
python3 $D $R patch '{"archive":{"keepUploads":false},"preferences":{"captureDelaySeconds":0}}' >/dev/null; sleep 2
python3 $D $R cli ui.show '{"view":"activity"}' >/dev/null; sleep 3; shot after-dash
python3 $D $R click 0 88 82 right >/dev/null; sleep 1.2; python3 $D $R move 0 150 104 >/dev/null; sleep 0.3; python3 $D $R move 0 200 136 >/dev/null; sleep 1.8; shot after-rail; key esc; key esc; sleep 0.5
python3 $D $R click 0 1098 778 right >/dev/null; sleep 1.2; python3 $D $R move 0 1100 469 >/dev/null; sleep 0.3; python3 $D $R move 0 1110 495 >/dev/null; sleep 1.8; shot after-tray; key esc; key esc; sleep 0.5
python3 $D $R cli ui.show '{"view":"settings"}' >/dev/null; sleep 2.5; python3 $D $R click 0 90 266 >/dev/null; sleep 1.8; shot after-shortcuts
# Captures need an output: keep a local copy from here on.
python3 $D $R local >/dev/null; sleep 2
python3 $D $R cli ui.show '{"view":"activity"}' >/dev/null; sleep 2
python3 $D $R invoke repeat | cut -c1-150; sleep 1.5; shot repeat-refusal
python3 $D $R click 0 1238 35 >/dev/null; sleep 0.5
python3 $D $R move 0 640 400 >/dev/null; id=$(python3 $D $R start desktop 5); sleep 2.2; shot countdown; python3 $D $R wait $id | cut -c1-100
