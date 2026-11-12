#!/bin/sh
# Closes notification popups left on the screen by earlier lab residents (Plasma keeps critical ones until dismissed).
export XDG_RUNTIME_DIR=/run/user/$(id -u) DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$(id -u)/bus
last=$(gdbus call --session --dest org.freedesktop.Notifications --object-path /org/freedesktop/Notifications --method org.freedesktop.Notifications.Notify "sf7" 0 "" "sf7 sweep" "" "[]" "{}" 1 | sed 's/^(uint32 //; s/[^0-9].*//')
i=$((last - 40)); [ "$i" -lt 1 ] && i=1
while [ "$i" -le "$last" ]; do gdbus call --session --dest org.freedesktop.Notifications --object-path /org/freedesktop/Notifications --method org.freedesktop.Notifications.CloseNotification "$i" > /dev/null 2>&1; i=$((i + 1)); done
echo "closed up to $last"
