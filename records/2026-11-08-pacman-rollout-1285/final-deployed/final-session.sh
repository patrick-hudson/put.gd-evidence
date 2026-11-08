#!/bin/bash
set -eu
pid=$(pgrep -u "$(id -u)" -x quickshell | head -1)
for name in OMARCHY_PATH DISPLAY WAYLAND_DISPLAY XDG_RUNTIME_DIR DBUS_SESSION_BUS_ADDRESS XDG_CURRENT_DESKTOP XDG_SESSION_TYPE HYPRLAND_INSTANCE_SIGNATURE; do
 value=$(tr '\0' '\n' < /proc/$pid/environ | sed -n "s/^$name=//p")
 [ -z "$value" ] || export "$name=$value"
done
curl -fsSL https://app.put.gd/install | sh -s -- --channel nightly
