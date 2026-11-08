#!/bin/bash
S=$(mktemp -d /w/runs/gdb-mc-XXXX); echo "$S"
export XDG_RUNTIME_DIR=$(mktemp -d /tmp/rt-XXXX); chmod 700 $XDG_RUNTIME_DIR
export XDG_CONFIG_HOME=$S/config XDG_DATA_HOME=$S/data XDG_STATE_HOME=$S/state XDG_CACHE_HOME=$S/cache S
mkdir -p $XDG_CONFIG_HOME
dbus-run-session -- bash -c '
 export WAYLAND_DISPLAY=wayland-77
 QT_QPA_PLATFORM=offscreen gdb -q -batch -x /w/kit/acq.gdb --args /w/magpie/b/bin/org.buddiesofbudgie.Magpie-0.0.1 --platform-display-libs mir:virtual --virtual-output 1920x1080 > $S/gdb.out 2>&1 & C=$!
 for i in $(seq 1 150); do [ -S $XDG_RUNTIME_DIR/wayland-77 ] && break; sleep 0.2; done; sleep 4
 foot -a win1 -T win1 -W 60x20 sh -c "while :; do date +%s.%N; sleep 0.05; done" > $S/foot.out 2>&1 & F=$!
 sleep 3
 echo gdb-attached >> $S/gdb.status
 /w/kit/mincap win1 12 3 500 > $S/mincap.out 2>&1
 kill $F; wait $F 2>/dev/null; sleep 1; pkillg=$(pgrep -P $C -n); kill -TERM $C; wait $C 2>/dev/null'
cut -d" " -f3- $S/mincap.out
