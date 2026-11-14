set -eu
cd "$HOME/work/s5202"
. ./session.env
label=$1
export XDG_CONFIG_HOME=$HOME/work/s5202/$label/config XDG_DATA_HOME=$HOME/work/s5202/$label/data XDG_CACHE_HOME=$HOME/work/s5202/$label/cache XDG_STATE_HOME=$HOME/work/s5202/$label/state XDG_RUNTIME_DIR=$HOME/work/s5202/$label/run PUTGD_RECORD_DEBUG_LOG=$HOME/work/s5202/$label/helper.log
mkdir -m 700 -p bin ff
cat > bin/cli-$label <<WRAP
#!/bin/sh
. "$HOME/work/s5202/session.env"
export XDG_CONFIG_HOME=$XDG_CONFIG_HOME XDG_DATA_HOME=$XDG_DATA_HOME XDG_CACHE_HOME=$XDG_CACHE_HOME XDG_STATE_HOME=$XDG_STATE_HOME XDG_RUNTIME_DIR=$XDG_RUNTIME_DIR
exec /usr/bin/putgd-cli "\$@"
WRAP
chmod 700 bin/cli-$label
if ! test -f template.json; then
 setsid nohup putgd --background > "$label/init.log" 2>&1 </dev/null & echo $! > "$label/init.pid"
 sleep 2
 bin/cli-$label settings.get > template.json
 bin/cli-$label ui.quit
 sleep 1
fi
python3 mkconfig.py template.json "$label"
setsid nohup putgd --background > "$label/resident.log" 2>&1 </dev/null & echo $! > "$label/resident.pid"
sleep 2
bin/cli-$label diagnostics > "$label/diagnostics.json"
python3 - "$label" <<'PY'
import sys,json
from pathlib import Path
l=Path.home()/'work/s5202';v=json.loads((l/sys.argv[1]/'diagnostics.json').read_text());assert v['ok'];(l/sys.argv[1]/'build.json').write_text(json.dumps(v['result']['build'],indent=2));print(v['result']['build'])
PY
if ! test -f firefox.pid || ! kill -0 $(cat firefox.pid) 2>/dev/null; then
 setsid nohup firefox --no-remote --profile "$HOME/work/s5202/ff" --kiosk https://en.wikipedia.org/wiki/Linux >firefox.log 2>&1 </dev/null & echo $! > firefox.pid
else
 firefox --profile "$HOME/work/s5202/ff" https://en.wikipedia.org/wiki/Linux
fi
sleep 6
python3 rfbshot.py "$label/browser-ready.png" --vnc 5900
