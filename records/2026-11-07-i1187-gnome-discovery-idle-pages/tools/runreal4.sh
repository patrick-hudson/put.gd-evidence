#!/bin/bash
# v4 condition: saved configuration, so no UI process. base vs fix v3, absent ABAB (300 s), then enabled base and fix.
set -u
cd ~/work/i1187
B=base775/squashfs-root; F=fix1187v3/squashfs-root; SC=$HOME/work/i1187/seed-config.json
run(){ timeout 600 python3 -I tools/m1187.py "$1" "$2" "out/$1" "$3" --real --seed-config $SC "${@:4}" > "out/$1.log" 2>&1; echo "$1 rc=$?" >> out/real4.progress; }
run nu-base-absent-b1 $B absent --secs 300
run nu-fix-absent-b1  $F absent --secs 300
run nu-base-absent-b2 $B absent --secs 300
run nu-fix-absent-b2  $F absent --secs 300
run nu-base-enabled   $B enabled --secs 240
run nu-fix-enabled    $F enabled --secs 240
DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$(id -u)/bus gnome-extensions enable putgd@put.gd
echo all-done >> out/real4.progress
