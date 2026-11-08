#!/bin/bash
# d69: is the slow window after an output appears put.gd's or Hyprland's? rows/rt2/
cd ~/work/d1275; R=d6; O=rows/rt2; mkdir -p $O; G="./gs.sh $R"; APP=/home/lab/putgd-final.AppImage
sy(){ $G "~/d/probe/hc bash -c \"(setsid nohup ~/d/probe/syncprobe /tmp/sync-$1.log >/dev/null 2>&1 </dev/null &)\""; sleep 1; }
syoff(){ $G "pkill -x syncprobe; sleep 0.3; cat /tmp/sync-$1.log" > $O/sync-$1.log; }
start(){ $G "~/d/probe/acc.py quit 2>&1 | tail -1 | head -c 30; sleep 2; rm -f ~/d/acc/resident.log"; $G "WAYLAND_DEBUG=1 ~/d/probe/acc.py start $1 | cut -c1-70; sleep 5; ~/d/probe/setkeys.py region=Ctrl+Shift+1 window=Ctrl+Shift+2 desktop=Ctrl+Shift+3 >/dev/null; ~/d/probe/hc ~/d/probe/win.py keep none >/dev/null; ~/d/probe/hc bash -c \"(setsid foot -T bench-foot >/dev/null 2>&1 </dev/null &)\""; sleep 3; }
log(){ $G "cat ~/d/acc/resident.log" > $O/$1.wl.log; python3 rt2sum.py $O/$1.jsonl $O/sync-$1.log $O/$1.wl.log | cut -c1-360 | tee $O/$1.table; }
{
echo "== build: $($G '~/d/probe/acc.py start '$APP' >/dev/null; sleep 5; ~/d/probe/acc.py cli diagnostics | python3 -c "import json,sys; print(json.load(sys.stdin)[\"result\"][\"build\"][\"version\"])"; ~/d/probe/acc.py quit | tail -1 | head -c 30')"
echo "== A. control: output appears, no put.gd running, 2 s window starting 1.5 s later (no hotkey)"; sy control; CONTROL=1 python3 rt.py $R 8 1.5 0.3 $O/control.jsonl 2>&1 | tail -1 | cut -c1-120; syoff control; python3 rt2sum.py $O/control.jsonl $O/sync-control.log | cut -c1-260 | tee $O/control.table
echo "== B. baseline: no output change, press 0.35 s after the hotkey, AppImage"; start $APP; sy baseline; NOOUT=1 python3 rt.py $R 8 1.5 0.3 $O/baseline.jsonl 2>&1 | tail -1 | cut -c1-120; syoff baseline; log baseline
echo "== C. output appears, press 0.35 s after the hotkey, AppImage"; start $APP; sy appimage; python3 rt.py $R 8 1.5 0.3 $O/appimage.jsonl 2>&1 | tail -1 | cut -c1-120; syoff appimage; log appimage
echo "== D. same, Arch package"; $G "~/d/probe/acc.py quit | tail -1 | head -c 30; sudo -n pacman -U --noconfirm ~/$(basename $(ls ci-final/release-native-archlinux/*.pkg.tar.zst)) >/dev/null 2>&1; pacman -Q putgd"; start /usr/bin/putgd; sy arch; python3 rt.py $R 8 1.5 0.3 $O/arch.jsonl 2>&1 | tail -1 | cut -c1-120; syoff arch; log arch
echo "== E. same, 6 s after the output appears (settled), Arch"; start /usr/bin/putgd; sy settled; python3 rt.py $R 8 6 0.3 $O/settled.jsonl 2>&1 | tail -1 | cut -c1-120; syoff settled; log settled
$G "~/d/probe/acc.py quit | tail -1 | head -c 30"; echo RT2-DONE
} 2>&1 | tee $O/rt2.log
