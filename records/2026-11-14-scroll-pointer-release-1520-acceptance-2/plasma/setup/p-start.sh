set -eu
cd "$HOME/work/s5202"
tar -xzf drivers.tgz
mkdir -m 700 -p bin ff b/config b/data b/cache b/state
chmod +x before.AppImage
./before.AppImage --appimage-extract > extract.log
cat > bin/cli-b <<EOF
#!/bin/sh
export LD_LIBRARY_PATH=$HOME/work/s5202/squashfs-root/usr/lib:$HOME/work/s5202/squashfs-root/usr/lib/putgd
exec $HOME/work/s5202/squashfs-root/usr/bin/putgd-cli "\$@"
EOF
cat > bin/qdbus6 <<'EOF'
#!/bin/sh
exec /usr/lib64/qt6/bin/qdbus "$@"
EOF
cat > bin/firefox <<'EOF'
#!/usr/bin/python3
import subprocess,sys,os
l=os.path.expanduser('~/work/s5202')
p=subprocess.Popen(['flatpak','run','--filesystem='+l,'org.mozilla.firefox','--profile',l+'/ff','--kiosk',sys.argv[-1]],stdout=subprocess.DEVNULL,stderr=open(l+'/firefox.log','a'),start_new_session=True)
EOF
chmod 700 bin/*
cat > ff/user.js <<'EOF'
user_pref("browser.aboutwelcome.enabled", false);
user_pref("browser.shell.checkDefaultBrowser", false);
user_pref("browser.startup.homepage_override.mstone", "ignore");
EOF
set -a; . ./session.env; set +a
export PATH=$HOME/work/s5202/bin:$PATH
python3 - <<'PY'
import os
for p in [os.environ['XDG_RUNTIME_DIR']+'/putgd/session.sock',os.environ['XDG_RUNTIME_DIR']+'/'+os.environ['WAYLAND_DISPLAY'],os.environ['XDG_RUNTIME_DIR']+'/bus']:
 print(p,len(p.encode()));assert len(p.encode())<=107
PY
export XDG_CONFIG_HOME=$HOME/work/s5202/b/config XDG_DATA_HOME=$HOME/work/s5202/b/data XDG_CACHE_HOME=$HOME/work/s5202/b/cache XDG_STATE_HOME=$HOME/work/s5202/b/state PUTGD_RECORD_DEBUG_LOG=$HOME/work/s5202/b/helper.log
setsid nohup ./squashfs-root/AppRun --background > b/init.log 2>&1 < /dev/null & echo $! > b/init.pid
sleep 3
bin/cli-b settings.get > template.json
bin/cli-b ui.quit
sleep 2
python3 mkconfig.py template.json b
setsid nohup ./squashfs-root/AppRun --background > b/resident.log 2>&1 < /dev/null & echo $! > b/resident.pid
firefox https://en.wikipedia.org/wiki/Linux
sleep 5
bin/cli-b diagnostics > b/diagnostics.json
flatpak ps --columns=instance,pid,application > flatpak-after-start.txt
python3 rfbshot.py b/browser-ready.png --vnc 5900
