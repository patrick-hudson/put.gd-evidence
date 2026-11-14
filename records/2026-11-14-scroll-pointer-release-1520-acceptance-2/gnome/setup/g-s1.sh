set -eu
cd "$HOME/work/s5202"
set -a; . ./session.env; set +a
label=$1
export XDG_CONFIG_HOME=$HOME/work/s5202/$label/config XDG_DATA_HOME=$HOME/work/s5202/$label/data XDG_CACHE_HOME=$HOME/work/s5202/$label/cache XDG_STATE_HOME=$HOME/work/s5202/$label/state
for i in 1 2 3; do
 uptime >> "$label/load.txt"
 python3 untouched.py "$HOME/work/s5202/bin/cli-$label" 470,200,980,720 https://en.wikipedia.org/wiki/Linux "$HOME/work/s5202/ff" "$label-$i" >> "$label/s1.jsonl" 2>> "$label/s1.err"
done
