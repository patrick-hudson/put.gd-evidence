#!/bin/sh
# One re-login on f44: restart GDM, wait for the Shell, leave the overview, restart the wall's VNC.
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus XDG_RUNTIME_DIR=/run/user/1000
sudo -n systemctl restart gdm
i=0; while [ $i -lt 40 ]; do sleep 1; pgrep -u patrick -x gnome-shell >/dev/null && break; i=$((i+1)); done
sleep 8
gdbus call --session -d org.gnome.Shell -o /org/gnome/Shell -m org.freedesktop.DBus.Properties.Set org.gnome.Shell OverviewActive "<false>" >/dev/null
systemctl --user restart putgd-gnome-vnc.service
sleep 3
echo "shell $(pgrep -u patrick -x gnome-shell) tty $(cat /sys/class/tty/tty0/active) vnc $(systemctl --user is-active putgd-gnome-vnc.service)"
