#!/bin/bash
# v2: base vs fix v2, extension absent ABAB (300 s), then fix v2 enabled and late enable
set -u
cd ~/work/i1187
B=base775/squashfs-root; F=fix1187v2/squashfs-root
run(){ timeout 480 python3 -I tools/m1187.py "$1" "$2" "out/$1" "$3" --real "${@:4}" > "out/$1.log" 2>&1; echo "$1 rc=$?" >> out/real2.progress; }
run v2-base-absent-b1 $B absent --secs 300
run v2-fix-absent-b1  $F absent --secs 300
run v2-base-absent-b2 $B absent --secs 300
run v2-fix-absent-b2  $F absent --secs 300
run v2-fix-enabled    $F enabled --secs 240
run v2-fix-late       $F absent --secs 240 --enable-at 150
DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$(id -u)/bus gnome-extensions enable putgd@put.gd
echo all-done >> out/real2.progress
