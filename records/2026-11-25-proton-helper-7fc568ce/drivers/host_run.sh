#!/bin/bash
# P6 rerun (#2025) on one builder, under `desktop_lock.py run HOST` (desktop) with the Proton lock and quiet
# lease already held by the same session. Usage:
#   host_run.sh HOST SESSION VNCPORT COMMIT HELPER_SHA PACKAGE PACKAGE_SHA FIRST_INDEX [install|noinstall] [memory|functional]
set -euo pipefail
host=$1 session=$2 port=$3 commit=$4 helper=$5 package=$6 packagesha=$7 n=$8 mode=$9 memory=${10}
D=$HOME/work/p6r/drivers
prefix=$(case $host in m74) echo p7m;; f44) echo p7f;; k72) echo p7k;; esac)
python3 $D/desktop_lock.py held --session "$session" >/dev/null
for r in proton quiet; do python3 $D/desktop_lock.py held --resource $r --session "$session" >/dev/null; done
if [ "$mode" = install ]; then python3 $D/install.py $D "$package" "$packagesha" "$helper" 2>&1 | tee -a $D/install-run.log; fi
full=$HOME/work/p6r/$prefix$n
args=(--app / --host "$host" --session "$session" --vnc-port "$port" --helper-sha256 "$helper" --commit "$commit")
[ "$memory" = memory ] && args+=(--memory)
python3 $D/proton_accept.py "${args[@]}" --work "$full" > $D/$prefix$n.log 2>&1 || { echo "functional/idle run $prefix$n failed"; tail -40 $D/$prefix$n.log; exit 1; }
tail -32 $D/$prefix$n.log
active=$HOME/work/p6r/$prefix$((n+1))
python3 $D/proton_accept.py --app / --host "$host" --session "$session" --vnc-port "$port" --helper-sha256 "$helper" --commit "$commit" \
  --work "$active" --only file-8m region-complete region-cancel revoke-all > $D/$prefix$((n+1)).log 2>&1 || { echo "active run failed"; tail -20 $D/$prefix$((n+1)).log; exit 1; }
tail -8 $D/$prefix$((n+1)).log
