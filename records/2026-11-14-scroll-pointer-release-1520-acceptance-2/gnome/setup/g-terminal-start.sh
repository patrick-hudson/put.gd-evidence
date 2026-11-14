set -eu
cd "$HOME/work/s5202"
set -a; . ./session.env; set +a
firefox --profile "$HOME/work/s5202/ff" https://en.wikipedia.org/wiki/Linux
sleep 5
VNC=5901 python3 terminal-check.py xterm > a/terminal-check.log 2>&1
