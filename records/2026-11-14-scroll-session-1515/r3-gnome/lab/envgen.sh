#!/bin/bash
# The desktop session's environment for processes started over SSH.
systemctl --user show-environment | grep -E '^(WAYLAND_DISPLAY|DISPLAY|XDG_SESSION_TYPE|XDG_CURRENT_DESKTOP|DBUS_SESSION_BUS_ADDRESS|XDG_RUNTIME_DIR)=' > $HOME/work/scroll-session/gnome/session.env
echo "QT_QPA_PLATFORM=wayland" >> $HOME/work/scroll-session/gnome/session.env
cat $HOME/work/scroll-session/gnome/session.env
