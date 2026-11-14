set -eu
cd "$HOME/work/s5302"
set -a; . ./session.env; set +a
export XDG_CONFIG_HOME=$HOME/work/s5302/a/config XDG_DATA_HOME=$HOME/work/s5302/a/data XDG_CACHE_HOME=$HOME/work/s5302/a/cache XDG_STATE_HOME=$HOME/work/s5302/a/state
python3 extra.py >a/double-resume-driver.log 2>&1
for i in $(seq 1 20); do
 if grep -q 'pointer put back by .* sent' a/helper.log; then break; fi
 firefox --profile "$HOME/work/s5302/ff" https://en.wikipedia.org/wiki/Linux
 sleep 5
 python3 correction-probe.py --rel --cli "$HOME/work/s5302/bin/cli-a" --rect 470,200,980,720 --stop 960,956 --vnc 5901 --log a/helper.log --start 1 --jitter 5 --label "g1-random-$i" >>a/correction-probes.jsonl 2>>a/correction-probes.err
done
firefox --profile "$HOME/work/s5302/ff" https://en.wikipedia.org/wiki/Linux
sleep 5
VNC=5901 python3 terminal-check.py xterm >a/terminal-check.log 2>&1
