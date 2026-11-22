#!/bin/bash
set -euo pipefail
root=$1
theme=$2
export XDG_CONFIG_HOME="$root/gconfig"
mkdir -p "$XDG_CONFIG_HOME"
id=7c147abe-093a-49d1-83d0-901225a19200
case "$theme" in
  solarized) bg=002b36; fg=839496 ;;
  github) bg=0d1117; fg=c9d1d9 ;;
  monokai) bg=272822; fg=f8f8f2 ;;
esac
if [[ ${3:-} == configure ]]; then
    dconf write /org/gnome/terminal/legacy/profiles:/list "['$id']"
    dconf write /org/gnome/terminal/legacy/profiles:/default "'$id'"
    p="/org/gnome/terminal/legacy/profiles:/:$id"
    dconf write "$p/visible-name" "'Quick redact fixture'"
    dconf write "$p/use-theme-colors" false
    dconf write "$p/use-system-font" false
    dconf write "$p/font" "'DejaVu Sans Mono 11'"
    dconf write "$p/background-color" "'#$bg'"
    dconf write "$p/foreground-color" "'#$fg'"
    dconf write "$p/scrollbar-policy" "'never'"
    dconf write "$p/audible-bell" false
    exit
fi
dbus-run-session -- "$0" "$root" "$theme" configure
app=org.gnome.Terminal.QrFixture
/usr/libexec/gnome-terminal-server --app-id "$app" &
server=$!
trap 'kill "$server" 2>/dev/null || true; wait "$server" || true' EXIT
for n in {1..80}; do
    result=$(gdbus call --session --dest org.freedesktop.DBus --object-path /org/freedesktop/DBus --method org.freedesktop.DBus.NameHasOwner "$app")
    [[ "$result" == '(true,)' ]] && break
    sleep .1
done
[[ "$result" == "(true,)" ]] || { echo "Private terminal server failed to own $app"; exit 1; }
/usr/bin/gnome-terminal.real --app-id "$app" --profile="$id" --full-screen --hide-menubar --title='Quick redact fixture' -- "$root/scripts/term.sh" "$root/fixture/$theme.txt" "$bg" "$fg"
wid=$(timeout 6s xdotool search --sync --onlyvisible --name '^Quick redact fixture$')
[[ "$wid" =~ ^[0-9]+$ ]]
wmctrl -ir "$(printf '0x%x' "$wid")" -b add,fullscreen
timeout 4s xdotool windowactivate --sync "$wid"
xdotool getwindowgeometry "$wid"
wait "$server"
