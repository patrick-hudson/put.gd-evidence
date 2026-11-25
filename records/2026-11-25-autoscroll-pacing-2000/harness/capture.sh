set -euo pipefail
umask 077
cd "$(realpath ~/work/i2000)"
export PYTHONDONTWRITEBYTECODE=1
head=$1; lane=$2; browser=$3; sites=$4
test -z "$(pgrep -x putgd-record || true)"
gnome-extensions list --enabled | grep -qx putgd@put.gd
gnome-extensions list --enabled | grep -qx appindicatorsupport@rgcjonas.gmail.com
export LAB_BUILD_DIR="$PWD/src-$head/build/release"
export LAB_HELPER="$PWD/pkg-$head/usr/bin/putgd-record"
export LAB_DIR="$PWD/$lane"
export LAB_X11=0 SF7_VNC=5901
mkdir "$LAB_DIR"
ln -s "$PWD/tools" "$LAB_DIR/tools"
export TMPDIR="$LAB_DIR/t" XDG_CONFIG_HOME="$LAB_DIR/c" XDG_CACHE_HOME="$LAB_DIR/k" XDG_DATA_HOME="$LAB_DIR/d" XDG_STATE_HOME="$LAB_DIR/s"
export XDG_RUNTIME_DIR="/run/user/$(id -u)"
mkdir "$TMPDIR"
python3 - <<'PY' | tee "$LAB_DIR/socket-lengths.txt"
import os
from pathlib import Path
tmp = Path(os.environ["TMPDIR"]); runtime = Path(os.environ["XDG_RUNTIME_DIR"]); user = os.environ["USER"]
for path in (runtime / "putgd/session.sock", tmp / "putgd/session.sock", tmp / f"runtime-{user}/putgd/session.sock", runtime / "pipewire-0", runtime / "wayland-0", runtime / "bus", tmp / "dbus-0000000000"):
    size = len(os.fsencode(path.resolve())); print(size, path.resolve())
    if size > 107: raise SystemExit("Unix socket path exceeds 107 bytes")
PY
cmp "$(find "$PWD/pkg-$head" -name build-info.json -print)" "$LAB_BUILD_DIR/build-identity/build-info.json"
cat "$LAB_BUILD_DIR/build-identity/build-info.json" | tee "$LAB_DIR/identity.json"
pgrep -x gnome-shell >/dev/null
gnome-extensions list --enabled > "$LAB_DIR/extensions.txt"
python3 -u sess.py "$browser" "$sites" auto
if [[ -n $(pgrep -x putgd-record || true) ]]; then echo 'Capture helper remains after harness exit' >&2; exit 1; fi
