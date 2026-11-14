set -eu
cd "$HOME/work/s5302"
tar -xzf drivers.tgz
python3 guest-prep.py > prep.log
set -a; . ./session.env; set +a
export PATH=$HOME/work/s5302/bin:$PATH
python3 - <<'PY'
import os
from pathlib import Path
r=os.environ['XDG_RUNTIME_DIR'];sig=os.environ['HYPRLAND_INSTANCE_SIGNATURE']
for p in [r+'/hypr/'+sig+'/.socket.sock',r+'/hypr/'+sig+'/.socket2.sock',r+'/'+os.environ['WAYLAND_DISPLAY'],r+'/putgd/session.sock',r+'/pipewire-0',r+'/bus']:print(p,len(p.encode()));assert len(p.encode())<=107
PY
chmod +x before.AppImage
./before.AppImage --appimage-extract > extract.log
cat > bin/cli-b <<EOF
#!/bin/sh
export LD_LIBRARY_PATH=$HOME/work/s5302/squashfs-root/usr/lib:$HOME/work/s5302/squashfs-root/usr/lib/putgd
exec $HOME/work/s5302/squashfs-root/usr/bin/putgd-cli "\$@"
EOF
chmod 700 bin/cli-b
export XDG_CONFIG_HOME=$HOME/work/s5302/b/config XDG_DATA_HOME=$HOME/work/s5302/b/data XDG_CACHE_HOME=$HOME/work/s5302/b/cache XDG_STATE_HOME=$HOME/work/s5302/b/state PUTGD_RECORD_DEBUG_LOG=$HOME/work/s5302/b/helper.log
setsid nohup ./squashfs-root/AppRun --background > b/init.log 2>&1 < /dev/null & echo $! > b/init.pid
sleep 3
bin/cli-b settings.get > template.json
bin/cli-b ui.quit
sleep 2
python3 mkconfig.py template.json b
setsid nohup ./squashfs-root/AppRun --background > b/resident.log 2>&1 < /dev/null & echo $! > b/resident.pid
firefox https://en.wikipedia.org/wiki/Linux
sleep 6
bin/cli-b diagnostics > b/diagnostics.json
hyprctl clients -j > b/clients-before.json
