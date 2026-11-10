#!/bin/sh
# pics-desktop.sh DESKTOP: tray menu, rail context menu and countdown pictures of one lab guest (run on its VM host).
# Writes /tmp/p1363-pics/raw-DESKTOP-{tray,rail,countdown}.png. Coordinates are those of the #1363 lab guests.
desk=$1; D=/tmp/p1363-vmdrive.py; cd $HOME/work/i1363; mkdir -p /tmp/p1363-pics
case $desk in
 kde) R=k64; K=$HOME/work/put.gd/work/lab-bootstrap-k72/identity;;
 gnome) R=g65; K=$HOME/work/put.gd/work/lab-bootstrap-m74/identity;;
 budgie) R=b63; K=$HOME/work/put.gd/work/lab-bootstrap-d69/identity;;
 hyprland) R=h63; K=$HOME/work/put.gd/work/lab-bootstrap-omarchy/identity;;
esac
key() { python3 tools/lab/lab.py key --run work/lab-runs/$R "$1" >/dev/null; }
shot() { /tmp/p1363-shot.sh $R $1 "$2" >/dev/null; cp /tmp/p1363-shots/$R-$2.png /tmp/p1363-pics/raw-$desk-$2.png; }
wl() { /tmp/p1363-gs.sh $R $K ". /tmp/env.sh; python3 /tmp/wayland_pointer.py $* --extent 2304 800"; }
show() { python3 $D $R cli ui.show "{\"view\":\"$1\"}" >/dev/null; sleep 3; }
case $desk in
 kde)
  # Tray on head 0 (bottom right), the window opens maximized on the pointer's head (head 1, at x 1280).
  python3 $D $R gclick 913 772 right >/dev/null; sleep 1.5; python3 $D $R gmove 975 420 >/dev/null; sleep 0.3; python3 $D $R gclick 980 427 >/dev/null; sleep 2.5; shot 0 tray; key esc; key esc; sleep 0.8
  python3 $D $R gmove 1700 400 >/dev/null; show activity
  python3 $D $R gclick 1368 82 right >/dev/null; sleep 1.5; python3 $D $R gmove 1420 104 >/dev/null; sleep 0.3; python3 $D $R gclick 1470 136 >/dev/null; sleep 2.5; shot 1 rail; key esc; key esc; sleep 0.8
  python3 $D $R gmove 1700 500 >/dev/null; id=$(python3 $D $R start desktop 5); sleep 2.2; shot 1 countdown; python3 $D $R wait $id | cut -c1-90;;
 gnome)
  python3 $D $R gclick 1156 14 >/dev/null; sleep 1.5; python3 $D $R gclick 1150 315 >/dev/null; sleep 2.5; shot 0 tray; key esc; sleep 0.8
  python3 $D $R gmove 600 400 >/dev/null; show activity
  python3 $D $R gclick 155 114 right >/dev/null; sleep 1.5; python3 $D $R gmove 210 136 >/dev/null; sleep 0.3; python3 $D $R gclick 260 168 >/dev/null; sleep 2.5; shot 0 rail; key esc; key esc; sleep 0.8
  python3 $D $R gmove 600 500 >/dev/null; id=$(python3 $D $R start desktop 5); sleep 2.2; shot 0 countdown; python3 $D $R wait $id | cut -c1-90;;
 budgie)
  # labwc: head 1 (1024x768) is at 0,0 and holds the panel; the window opens there.
  wl click 842 750 --button right; sleep 1.5; wl move 700 420; sleep 0.3; wl move 690 434; sleep 2.5; shot 1 tray; key esc; key esc; sleep 0.8
  wl move 500 400; show activity
  wl click 88 82 --button right; sleep 1.5; wl move 150 104; sleep 0.3; wl move 200 136; sleep 2.5; shot 1 rail; key esc; key esc; sleep 0.8
  wl move 500 500; id=$(python3 $D $R start desktop 5); sleep 2.2; shot 1 countdown; python3 $D $R wait $id | cut -c1-90;;
 hyprland)
  # Omarchy: the tray sits behind the "<" in the bar; its menu closes on a click elsewhere, not on Escape.
  # The window is tiled over head 0.
  # The tray opens when the pointer rests on the "<" (x 1151); the icons then slide in and put.gd's is at
  # x 1124. A click at 1151 at that moment hits another tray icon, so only move there.
  wl move 700 300; sleep 0.5; wl move 1151 13; sleep 1.2; wl move 1124 13; sleep 0.6; wl click 1124 13 --button right; sleep 1.0; wl move 1100 265; sleep 0.8; shot 0 tray; wl click 400 500; sleep 1
  wl move 600 400; show activity
  wl click 100 120 --button right; sleep 1.5; wl move 160 142; sleep 0.3; wl move 210 174; sleep 2.5; shot 0 rail; key esc; key esc; sleep 0.8
  wl move 600 500; id=$(python3 $D $R start desktop 5); sleep 2.2; shot 0 countdown; python3 $D $R wait $id | cut -c1-90;;
esac
