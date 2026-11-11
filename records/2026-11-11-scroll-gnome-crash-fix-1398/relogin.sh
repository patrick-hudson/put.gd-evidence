#!/bin/sh
# Restart GDM (reloads the Shell and its extensions), leave the overview, restart the wall VNC.
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus XDG_RUNTIME_DIR=/run/user/1000
gsettings set org.gnome.shell disable-user-extensions false
sudo -n systemctl restart gdm
i=0; while [ $i -lt 40 ]; do sleep 1; pgrep -u patrick -x gnome-shell >/dev/null && break; i=$((i+1)); done
sleep 8
gdbus call --session -d org.gnome.Shell -o /org/gnome/Shell -m org.freedesktop.DBus.Properties.Set org.gnome.Shell OverviewActive "<false>" >/dev/null
systemctl --user restart putgd-gnome-vnc.service
sleep 3
echo "shell $(pgrep -u patrick -x gnome-shell) vt $(cat /sys/class/tty/tty0/active)"
gnome-extensions info putgd@put.gd | grep -i "state\|version"
