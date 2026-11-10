#!/bin/bash
set -u
export XDG_RUNTIME_DIR=/run/user/1000 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus
root=/var/home/patrick/a1364
q() { gdbus call --session --dest org.kde.KWin --object-path /Effects --method org.kde.kwin.Effects.$1 mouseclick; }
for mode in ${MODES:-stop cancel kill}; do
 for state in notloaded loadedoff loadedon; do
  q unloadEffect >/dev/null
  if [ "$state" != notloaded ]; then q loadEffect >/dev/null; fi
  if [ "$state" = loadedon ]; then gdbus call --session --dest org.kde.kglobalaccel --object-path /component/kwin --method org.kde.kglobalaccel.Component.invokeShortcut ToggleMouseClick >/dev/null; fi
  sleep .5
  name=${PREFIX:-life}-$mode-$state
  { q isEffectLoaded; q supportInformation; } > "$root/runs/$name-before.txt"
  python3 "$root/effects2.py" "$mode" --run "$root/runs/$name" --build "pr=$root/pr.AppImage" --analyzer "$root/analyzer/squashfs-root" --video marker --rounds 1 --no-notifications --keep-unpaired --real-data-home --frames --target monitor --format mp4 --mic off --system tone --lead 3 --pause-for 0 --pause-at 14 --after 2 --click 4,300,100,left --click 8,700,100,right --click 12,1100,100,middle > "$root/runs/$name.out" 2>&1
  echo "$name rc=$?"
  { q isEffectLoaded; q supportInformation; } > "$root/runs/$name-after.txt"
  diff -u "$root/runs/$name-before.txt" "$root/runs/$name-after.txt" || true
 done
done
q unloadEffect
