#!/bin/bash
# Headless Magpie + moving foot; mincap sessions (one connection, or RECONNECT=1 for one process per session as put.gd's helper does).
S=$(mktemp -d /w/runs/${TAG:-mc}-XXXX); echo "$S"
export XDG_RUNTIME_DIR=$(mktemp -d /tmp/rt-XXXX); chmod 700 $XDG_RUNTIME_DIR
export XDG_CONFIG_HOME=$S/config XDG_DATA_HOME=$S/data XDG_STATE_HOME=$S/state XDG_CACHE_HOME=$S/cache S
mkdir -p $XDG_CONFIG_HOME
export N=${N:-16} SECS=${SECS:-3} GAP=${GAP:-500} RECONNECT=${RECONNECT:-0}
dbus-run-session -- bash -c '
 export WAYLAND_DISPLAY=wayland-77
 QT_QPA_PLATFORM=offscreen /w/magpie/b/bin/org.buddiesofbudgie.Magpie-0.0.1 --platform-display-libs mir:virtual --virtual-output 1920x1080 > $S/compositor.log 2>&1 & C=$!
 for i in $(seq 1 50); do [ -S $XDG_RUNTIME_DIR/wayland-77 ] && break; sleep 0.2; done; sleep 2
 foot -a win1 -T win1 -W 60x20 sh -c "while :; do date +%s.%N; sleep 0.05; done" > $S/foot.out 2>&1 & F=$!
 sleep 3
 if [ "$RECONNECT" = 1 ]; then for i in $(seq 1 $N); do /w/kit/mincap win1 1 $SECS 0; python3 -c "import time;time.sleep($GAP/1000)"; done > $S/mincap.out 2>&1
 else /w/kit/mincap win1 $N $SECS $GAP > $S/mincap.out 2>&1; fi
 kill $F; wait $F 2>/dev/null; kill $C; wait $C 2>/dev/null'
cut -d" " -f3- $S/mincap.out
