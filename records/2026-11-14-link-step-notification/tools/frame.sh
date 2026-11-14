#!/bin/sh
# usage: frame.sh <before|after>  (run on d69 under the desktop lock)
set -u
W=$HOME/work/sweep-w8/harness; L=$1; O=$W/out-$L; mkdir -p "$O"
mkdir -m 700 -p $W/xdg-$L/config $W/xdg-$L/data $W/xdg-$L/state $W/xdg-$L/cache
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus XDG_RUNTIME_DIR=/run/user/1000 WAYLAND_DISPLAY=wayland-0 QT_QPA_PLATFORM=wayland
export XDG_CONFIG_HOME=$W/xdg-$L/config XDG_DATA_HOME=$W/xdg-$L/data XDG_STATE_HOME=$W/xdg-$L/state XDG_CACHE_HOME=$W/xdg-$L/cache TMPDIR=$W/xdg-$L/cache
dbus-monitor --session "type='method_call',interface='org.freedesktop.Notifications',member='Notify'" "type='method_return'" > "$O/monitor.txt" 2>/dev/null &
MON=$!
sleep 1
"$W/bin-$L/link_notice_harness" 9000 > "$O/harness.log" 2>&1 &
H=$!
sleep 5
python3 $HOME/work/sweep-w8/src/tools/lab/rfb.py 5900 "$O/frame.png" > "$O/rfb.txt" 2>&1
wait $H
kill $MON
python3 - "$O/monitor.txt" > "$O/ids.txt" <<'PY'
import re,sys
lines=open(sys.argv[1]).read().splitlines(); serials=set(); ids=[]
for i,l in enumerate(lines):
    m=re.search(r'method call .* serial=(\d+) .*member=Notify',l)
    if m: serials.add(m.group(1))
    m=re.search(r'method return .* reply_serial=(\d+)',l)
    if m and m.group(1) in serials and i+1<len(lines):
        v=re.search(r'uint32 (\d+)',lines[i+1])
        if v: ids.append(v.group(1))
print(' '.join(ids))
PY
for id in $(cat "$O/ids.txt"); do gdbus call --session --dest org.freedesktop.Notifications --object-path /org/freedesktop/Notifications --method org.freedesktop.Notifications.CloseNotification "$id" >/dev/null && echo "closed $id"; done
grep -i "invoked" "$O/harness.log"; cat "$O/rfb.txt"
