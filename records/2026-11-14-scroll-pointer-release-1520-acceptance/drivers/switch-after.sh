#!/bin/bash
set -eu
cd "$HOME/work/s1520"
set -a; . ./session.env; set +a
bin/cli-b ui.quit
for i in $(seq 1 30); do test ! -S "$XDG_RUNTIME_DIR/putgd/session.sock" && break; sleep .2; done
mkdir -m 700 -p after a/config a/data a/cache a/state
(cd after; chmod +x ../after.AppImage; ../after.AppImage --appimage-extract > extract.log)
cat > bin/cli-a <<EOF
#!/bin/sh
export LD_LIBRARY_PATH=$HOME/work/s1520/after/squashfs-root/usr/lib:$HOME/work/s1520/after/squashfs-root/usr/lib/putgd
exec $HOME/work/s1520/after/squashfs-root/usr/bin/putgd-cli "\$@"
EOF
chmod 700 bin/cli-a
python3 mkconfig.py template.json a
export XDG_CONFIG_HOME=$HOME/work/s1520/a/config XDG_DATA_HOME=$HOME/work/s1520/a/data XDG_CACHE_HOME=$HOME/work/s1520/a/cache XDG_STATE_HOME=$HOME/work/s1520/a/state PUTGD_RECORD_DEBUG_LOG=$HOME/work/s1520/a/helper.log
setsid nohup ./after/squashfs-root/AppRun --background > a/resident.log 2>&1 < /dev/null & echo $! > a/resident.pid
sleep 3
bin/cli-a diagnostics > a/diagnostics.json
python3 - <<'PY'
import json
v=json.load(open('a/diagnostics.json'));b=v['result']['build'];print(b);assert b['gitTree']=='9513f33d6ffdb474b4e8937a7da83bd840886574'
json.dump(b,open('a/build.json','w'),indent=2)
PY
