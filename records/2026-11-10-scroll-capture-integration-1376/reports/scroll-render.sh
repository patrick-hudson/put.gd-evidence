#!/bin/bash
set -eu
cd /home/patrick/work/scroll-integrate-1376
render_root=$(mktemp -d /tmp/scat1376.XXXXXX)
echo "$render_root" > catalog-path.log
mkdir -m 700 "$render_root/r"
python3 tools/diagnostics/check_socket_paths.py --socket "$render_root/r/putgd/session.sock"
env -u DISPLAY -u WAYLAND_DISPLAY -u DBUS_SESSION_BUS_ADDRESS QT_QPA_PLATFORM=offscreen XDG_RUNTIME_DIR="$render_root/r" XDG_CONFIG_HOME="$render_root/c" XDG_DATA_HOME="$render_root/d" XDG_STATE_HOME="$render_root/s" PUTGD_CATALOG_RECORD_ONLY=1 PUTGD_CATALOG_DATA_DIR="$render_root/data" build/dev/putgd-ui-catalog "$render_root/out" > "$render_root/render.log" 2>&1
python3 - "$render_root" <<'PY'
import pathlib,sys
p=pathlib.Path(sys.argv[1])
for s in ['ready','scrollingToTop','capturing','finishing']:
 f=p/'out'/('scroll-bar-'+s+'.png');assert f.stat().st_size>1000,f
print('PASS four catalog scroll bar states',p)
PY
