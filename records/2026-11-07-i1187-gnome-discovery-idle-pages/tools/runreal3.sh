#!/bin/bash
# v3: base vs fix v3, extension absent ABAB (300 s), then v3 enabled, then v3 late enable + capture
set -u
cd ~/work/i1187
B=base775/squashfs-root; F=fix1187v3/squashfs-root
run(){ timeout 600 python3 -I tools/m1187.py "$1" "$2" "out/$1" "$3" --real "${@:4}" > "out/$1.log" 2>&1; echo "$1 rc=$?" >> out/real3.progress; }
run v3-base-absent-b1 $B absent --secs 300
run v3-fix-absent-b1  $F absent --secs 300
run v3-base-absent-b2 $B absent --secs 300
run v3-fix-absent-b2  $F absent --secs 300
run v3-fix-enabled    $F enabled --secs 240
run v3-fix-late       $F absent --secs 240 --enable-at 150 --capture-after
DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$(id -u)/bus gnome-extensions enable putgd@put.gd
echo all-done >> out/real3.progress
