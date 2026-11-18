#!/bin/bash
# start|stop a private resident for #1618 acceptance. Env from the desktop session.
R=/run/user/$(id -u)/qr
W=$HOME/work/qr1618/state
case $1 in
start)
 mkdir -p $R $W/config $W/data $W/state $W/cache $W/out; chmod 700 $R
 if [ -n "$SESSION_PROC" ]; then pp=$(pgrep -u $(id -u) -x $SESSION_PROC | head -1); unset WAYLAND_DISPLAY DISPLAY XAUTHORITY; eval "$(tr '\0' '\n' < /proc/$pp/environ | grep -E '^(DISPLAY|WAYLAND_DISPLAY|XDG_SESSION_TYPE|XDG_CURRENT_DESKTOP|XAUTHORITY)=' | sed 's/^/export /; s/=/="/; s/$/"/')"; else
 eval "$(systemctl --user show-environment | grep -E '^(DISPLAY|WAYLAND_DISPLAY|XDG_SESSION_TYPE|XDG_CURRENT_DESKTOP|XAUTHORITY)=' | sed 's/^/export /; s/=/="/; s/$/"/')"; fi
 case "$WAYLAND_DISPLAY" in /*) ;; ?*) export WAYLAND_DISPLAY=/run/user/$(id -u)/$WAYLAND_DISPLAY;; esac
 export XDG_CONFIG_HOME=$W/config XDG_DATA_HOME=$W/data XDG_STATE_HOME=$W/state XDG_CACHE_HOME=$W/cache XDG_RUNTIME_DIR=$R
 export PIPEWIRE_RUNTIME_DIR=/run/user/$(id -u) PULSE_SERVER=unix:/run/user/$(id -u)/pulse/native
 rm -f $R/putgd/session.sock
 XDG_RUNTIME_DIR=/run/user/$(id -u) setsid -f systemd-run --user --scope --unit=qr1618-resident -E XDG_CONFIG_HOME -E XDG_DATA_HOME -E XDG_STATE_HOME -E XDG_CACHE_HOME -E XDG_RUNTIME_DIR=$R -E PIPEWIRE_RUNTIME_DIR -E PULSE_SERVER -E WAYLAND_DISPLAY -E DISPLAY -E XDG_SESSION_TYPE -E XDG_CURRENT_DESKTOP /usr/bin/putgd --background > $W/resident.log 2>&1 < /dev/null
 sleep 4; echo started; cat $W/resident.log | head;;
stop)
 systemctl --user stop qr1618-resident.scope; echo stopped;;
esac
