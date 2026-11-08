#!/bin/bash
# Headless compositor session (COMP=magpie|labwc) running wdrive.py. Results in $S.
# Env: BUILD (dir with putgd, putgd-cli, putgd-record), RUNS, CONTENT=static|motion, TAG
S=$(mktemp -d /w/runs/${TAG:-run}-XXXX); echo "$S"
export XDG_RUNTIME_DIR=$(mktemp -d /tmp/rt-XXXX); chmod 700 $XDG_RUNTIME_DIR
export XDG_CONFIG_HOME=$S/config XDG_DATA_HOME=$S/data XDG_STATE_HOME=$S/state XDG_CACHE_HOME=$S/cache
export S PUTGD_RECORD_DEBUG_LOG=$S/record-debug.log
mkdir -p $XDG_CONFIG_HOME/budgie-desktop/labwc $S/archive
export XDG_CURRENT_DESKTOP=Budgie XDG_SESSION_TYPE=wayland
if [ "${COMP:-magpie}" = magpie ]; then
dbus-run-session -- bash -c '
 export WAYLAND_DISPLAY=wayland-77
 QT_QPA_PLATFORM=offscreen /w/magpie/b/bin/org.buddiesofbudgie.Magpie-0.0.1 --platform-display-libs mir:virtual --virtual-output 1920x1080 > $S/compositor.log 2>&1 & C=$!
 for i in $(seq 1 50); do [ -S $XDG_RUNTIME_DIR/wayland-77 ] && break; sleep 0.2; done; sleep 2
 export QT_QPA_PLATFORM="wayland;xcb"
 python3 /w/kit/${DRIVER:-wdrive.py}
 kill $C; wait $C'
else
export WLR_BACKENDS=headless WLR_RENDERER=pixman WLR_LIBINPUT_NO_DEVICES=1 WLR_HEADLESS_OUTPUTS=1 QT_QPA_PLATFORM="wayland;xcb"
cp /usr/share/budgie-desktop/labwc/rc.xml $XDG_CONFIG_HOME/budgie-desktop/labwc/; cp /usr/share/budgie-desktop/labwc/menu.xml $XDG_CONFIG_HOME/budgie-desktop/labwc/ 2>/dev/null
dbus-run-session -- labwc --config-dir $XDG_CONFIG_HOME/budgie-desktop/labwc -S "python3 /w/kit/${DRIVER:-wdrive.py}" > $S/compositor.log 2>&1
fi
cat $S/result.log
