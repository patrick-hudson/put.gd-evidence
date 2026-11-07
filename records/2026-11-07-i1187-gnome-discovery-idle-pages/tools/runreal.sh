#!/bin/bash
# usage: runreal.sh — real f44 GNOME session, nightly base then fix: enabled, absent, absent->enable@150 (fix and base)
set -u
cd ~/work/i1187
B=base775/squashfs-root; F=fix1187/squashfs-root
run(){ timeout 420 python3 -I tools/m1187.py "$1" "$2" "out/$1" "$3" --secs 240 --real "${@:4}" > "out/$1.log" 2>&1; echo "$1 rc=$?" >> out/real.progress; }
run real-base-enabled $B enabled
run real-base-absent  $B absent
run real-fix-enabled  $F enabled
run real-fix-absent   $F absent
run real-fix-late     $F absent --enable-at 150
run real-base-late    $B absent --enable-at 150
DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$(id -u)/bus gnome-extensions enable putgd@put.gd
echo all-done >> out/real.progress
