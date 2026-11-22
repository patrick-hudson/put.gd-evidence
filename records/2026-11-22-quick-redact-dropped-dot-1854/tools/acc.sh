#!/bin/sh
# usage: acc.sh LABEL DEB TREE LEADER RESTORE_DEB   (on the desktop host, under its lock)
set -u
L=$1 DEB=$2 TREE=$3 LEADER=$4 RESTORE=$5
cd ~/r54
log(){ echo "[$(date -u +%T)] $*"; }
plan=$(sudo -n apt-get install -s --allow-downgrades "$DEB" 2>&1 | grep -E "^(Inst|Remv)")
echo "$plan"; if echo "$plan" | grep -vq "^Inst putgd "; then log "refusing: transaction touches more than putgd"; exit 3; fi
sudo -n apt-get install -y --allow-downgrades "$DEB" > apt-$L.log 2>&1 || { log install failed; exit 4; }
log "installed $(dpkg-query -W putgd)"
mkdir -p run-$L; rm -f run-$L/c.sock
setsid python3 tools/driver.py ~/r54/run-$L --leader $LEADER --vnc 5900 --tree $TREE > driver-$L.log 2>&1 < /dev/null &
DP=$!
i=0; while [ ! -S run-$L/c.sock ] && [ $i -lt 60 ]; do sleep 1; i=$((i+1)); done
timeout 300 python3 tools/dc.py run-$L/c.sock '["start"]' | head -c 400; echo
sleep 3
closemain(){
 if [ "$LEADER" = cinnamon ]; then
  export DISPLAY=:0 XAUTHORITY=$(tr "\0" "\n" < /proc/$(pgrep -u patrick -x cinnamon | head -1)/environ | grep ^XAUTHORITY= | cut -d= -f2)
  for w in $(wmctrl -l | awk '$4=="put.gd" && NF==4 {print $1}'); do wmctrl -i -c $w; done
 else
  cat > /tmp/r54-close.js <<'JS'
for (const w of workspace.windowList()) { if (w.caption === "put.gd") w.closeWindow(); }
JS
  export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$(id -u)/bus
  id=$(qdbus6 org.kde.KWin /Scripting org.kde.kwin.Scripting.loadScript /tmp/r54-close.js r54close); qdbus6 org.kde.KWin /Scripting/Script$id org.kde.kwin.Script.run >/dev/null 2>&1; sleep 1; qdbus6 org.kde.KWin /Scripting org.kde.kwin.Scripting.unloadScript r54close >/dev/null 2>&1
 fi
}
closemain; sleep 2
for leg in "" "--sensitive"; do
 name=$L; [ -n "$leg" ] && name=$L-up
 timeout 600 python3 tools/leg.py ~/r54/run-$L ~/r54/fx $name $leg > leg-$name.log 2>&1 || { log "leg $name failed, retrying after closing windows"; tail -3 leg-$name.log; closemain; sleep 2; timeout 600 python3 tools/leg.py ~/r54/run-$L ~/r54/fx $name $leg > leg-$name.log 2>&1 || { log "leg $name failed again"; tail -5 leg-$name.log; }; }
 log "leg $name: $(ls run-$L/out | grep -c "$name")"
done
timeout 60 python3 tools/dc.py run-$L/c.sock '["exit"]'; sleep 4
kill $DP 2>/dev/null
sudo -n apt-get install -y --allow-downgrades "$RESTORE" > apt-$L-restore.log 2>&1; log "restored $(dpkg-query -W putgd)"
pgrep -u patrick -a "putgd|viewer.py|driver.py" | head
