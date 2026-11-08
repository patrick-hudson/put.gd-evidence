#!/bin/bash
# d69: early drags through the press catcher on scaled, rotated and mixed-density outputs, and the catcher's end paths. Final head's packages. Output rows/scaled/
cd ~/work/d1275; R=d6; O=rows/bar; mkdir -p $O; G="./gs.sh $R"
APP=$(ls $PWD/ci-final/release-appimage/*.AppImage); ARCH=$(ls $PWD/ci-final/release-native-archlinux/*.pkg.tar.zst)
ev(){ $G "~/d/probe/hc ~/d/probe/hipc.py 'eval $1'" >/dev/null; }
ipc(){ $G "~/d/probe/hc ~/d/probe/hipc.py '$1'" >/dev/null; }
mon(){ $G '~/d/probe/hc ~/d/probe/hipc.py "j/monitors all" | python3 -c "import json,sys; [print(\" \", m[\"name\"], m[\"width\"], m[\"height\"], \"at\", m[\"x\"], m[\"y\"], \"scale\", m[\"scale\"], \"transform\", m[\"transform\"]) for m in json.load(sys.stdin)]"'; }
foot(){ $G '~/d/probe/hc ~/d/probe/win.py keep none >/dev/null; ~/d/probe/hc bash -c "(setsid foot -T bench-foot >/dev/null 2>&1 </dev/null &)"'; sleep 3; }
start(){ $G "for i in \$(seq 40); do pgrep -x quickshell >/dev/null && break; sleep 1; done; sleep 2; ~/d/probe/acc.py start $1 | cut -c1-90; sleep 4; ~/d/probe/setkeys.py region=Ctrl+Shift+1 window=Ctrl+Shift+2 desktop=Ctrl+Shift+3 >/dev/null"; }
quit(){ $G '~/d/probe/acc.py quit 2>&1 | tail -1'; }
base(){ ev 'hl.monitor({ output = "Virtual-1", mode = "1280x800@60", position = "0x0", scale = 1, transform = 0 })'; sleep 3; }
sweep(){ # label outputs W H
 local l=$1; shift; TRIALS=4 ./selsweep.sh $R $1 $2 $3 $O/$P-$l.log 0.1 0.3 1.5; }
one(){ # label binary
 P=$1; echo "##### $1: $($G '~/d/probe/acc.py start '$2' >/dev/null; sleep 5; ~/d/probe/acc.py local >/dev/null; ~/d/probe/acc.py cli diagnostics | python3 -c "import json,sys; print(json.load(sys.stdin)[\"result\"][\"build\"][\"version\"])"')"; quit; start $2
 echo "== scale 1.25, 1920x1080"; ev 'hl.monitor({ output = "Virtual-1", mode = "1920x1080@60", position = "0x0", scale = 1.25 })'; sleep 4; mon; foot; sweep scale125 1 1920 1080
 echo "== 90 degrees (transform 1), 1280x800"; ev 'hl.monitor({ output = "Virtual-1", mode = "1280x800@60", position = "0x0", scale = 1, transform = 1 })'; sleep 4; mon; foot; sweep rot90 1 800 1280
 base; echo "== mixed density: Virtual-1 scale 1, PUTGD-2 1024x768 scale 2"; ipc 'output create headless PUTGD-2'; sleep 1; ev 'hl.monitor({ output = "PUTGD-2", mode = "1024x768@60", position = "1280x0", scale = 2 })'; sleep 8; mon; foot
 $G "mkdir -p /tmp/watch /tmp/refs; rm -f /tmp/watch.stop; ~/d/probe/hc bash -c \"(setsid nohup bash -c 'while [ ! -e /tmp/watch.stop ]; do T=\\$(date +%s.%3N); grim -l 1 -o PUTGD-2 /tmp/watch/\\$T.png 2>/dev/null; sleep 0.6; done' >/dev/null 2>&1 </dev/null &)\""; echo "-- drag on the scale 1 output"; REFARG="-o Virtual-1" sweep mixed-virtual1 2 1792 800
 echo "-- drag on the scale 2 output"; COORDS="1380 100 1680 300" EXPECT=600x400 CMPRECT="200 200 600 400" REFARG="-o PUTGD-2" sweep mixed-scale2 2 1792 800
 $G "touch /tmp/watch.stop"; ipc 'output remove PUTGD-2'; sleep 1; base; mon; foot
 echo "== right button on the catcher"; python3 catcher_edge.py $R right-early 4 2>&1 | tee $O/$P-right.log | tail -1
 echo "== output removed during an early drag"; python3 catcher_edge.py $R output-gone 3 2>&1 | tee $O/$P-output-gone.log | tail -1
 quit
}
{
$G "sudo -n pacman -R --noconfirm putgd >/dev/null 2>&1; pacman -Q putgd 2>&1 | cut -c1-40"
$G "~/d/probe/hc bash -c \"(setsid nohup dbus-monitor --session 'interface=org.freedesktop.Notifications' > /tmp/notify.log 2>&1 </dev/null &)\""
one appimage /home/lab/putgd-final.AppImage
echo BAR-DONE
} 2>&1 | tee $O/scaled.log
