set -eu
cd "$HOME/work/s5202"
set -a; . ./session.env; set +a
export PATH=$HOME/work/s5202/bin:$PATH LANG=C.UTF-8
for label in b a; do
 if test "$label" = a; then bash switch-after.sh > switch-after.log 2>&1; fi
 export XDG_CONFIG_HOME=$HOME/work/s5202/$label/config XDG_DATA_HOME=$HOME/work/s5202/$label/data XDG_CACHE_HOME=$HOME/work/s5202/$label/cache XDG_STATE_HOME=$HOME/work/s5202/$label/state
 hyprctl clients -j > "$label/clients-s1.json"
 python3 - <<'PY'
import json,subprocess
v=json.loads(subprocess.check_output(['hyprctl','clients','-j'],text=True));assert not any(c.get('mapped') and c.get('class','').startswith('putgd') for c in v),v
PY
 for i in 1 2 3; do
  uptime >> "$label/load.txt"
  python3 untouched.py "$HOME/work/s5202/bin/cli-$label" 470,200,980,720 https://en.wikipedia.org/wiki/Linux "$HOME/work/s5202/chromium" "$label-$i" >> "$label/s1.jsonl" 2>> "$label/s1.err"
 done
done
