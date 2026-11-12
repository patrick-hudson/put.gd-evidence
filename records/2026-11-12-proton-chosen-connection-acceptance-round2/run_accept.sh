#!/bin/bash
# run_accept.sh HOST SESSION PACKAGE RUN_NAME [WAIT_MINUTES] [-- extra proton_accept.py arguments]
# Runs the Proton desktop acceptance script on one builder's live desktop, from the workstation.
# Takes the builder's desktop lock and Proton lock first and stops if either is refused.
set -u
HOST=$1; SESSION=$2; PACKAGE=$3; RUN=$4; WAIT=${5:-0}
shift 4; [ $# -gt 0 ] && shift; [ "${1:-}" = "--" ] && shift
EXTRA=("$@")
declare -A IP=([d69]=192.168.68.69 [f44]=192.168.68.70 [k72]=192.168.68.72 [m74]=192.168.68.74 [aurora-amd]=192.168.68.71)
REPO=/tmp/p1414-final
HERE=$(cd "$(dirname "$0")" && pwd)
OUT=$HERE/accept-results/$HOST/$RUN
SSH=(ssh -i /home/patrick/.ssh/awskey_110724 -o IdentitiesOnly=yes -o StrictHostKeyChecking=yes -o BatchMode=yes -o ConnectTimeout=15 -o UserKnownHostsFile=/home/patrick/work/put.gd/work/remote-builders/$HOST/known_hosts patrick@${IP[$HOST]})
lock() { python3 $REPO/desktop_lock.py "$@"; }
[ "$RUN" != lock-only ] && [ -e "$OUT" ] && { echo "STOP: $OUT exists; choose a new RUN_NAME"; exit 2; }
[ -f "$PACKAGE" ] || { echo "STOP: no package $PACKAGE"; exit 2; }

# 1. Both locks, or nothing. Wait politely for another session to finish; never break a lock.
deadline=$(( $(date +%s) + WAIT * 60 ))
while :; do
  if lock acquire $HOST --owner proton-accept --session $SESSION --purpose "Proton upload desktop acceptance PR #1414 65c9292f; private profile, lab account, no VMs" --minutes 45 >/tmp/pacc-$SESSION.lock 2>&1; then break; fi
  if lock status $HOST 2>/dev/null | grep -q "($SESSION)"; then break; fi   # already ours
  [ $(date +%s) -ge $deadline ] && { echo "STOP: the $HOST desktop lock is not available:"; lock status $HOST | head -5; exit 3; }
  sleep 60
done
if ! lock acquire $HOST --resource proton --owner proton-accept --session $SESSION --purpose "Proton upload desktop acceptance PR #1414 65c9292f" --minutes 45 >/dev/null 2>&1 \
   && ! lock status $HOST --resource proton | grep -q "($SESSION)"; then
  echo "STOP: the $HOST Proton lock is not available:"; lock status $HOST --resource proton | head -4
  lock release $HOST --session $SESSION --verified-clean | head -1; exit 3
fi
lock status $HOST | sed -n 1,2p; lock status $HOST --resource proton | sed -n 1,2p
[ "$RUN" = lock-only ] && { echo "LOCKS HELD by $SESSION; run again with a run name within 40 minutes"; exit 0; }

heartbeat() {
  while sleep 60; do
    lock heartbeat "$HOST" --session "$SESSION" >/dev/null
    lock heartbeat "$HOST" --resource proton --session "$SESSION" >/dev/null
  done
}
heartbeat & HEARTBEAT_PID=$!
trap 'kill "$HEARTBEAT_PID" 2>/dev/null || true' EXIT

# 2. Files onto the builder, in a private scratch folder.
"${SSH[@]}" "mkdir -m 700 ~/work/pf65" || { echo "STOP: cannot reach $HOST"; exit 4; }
scp -q -i /home/patrick/.ssh/awskey_110724 -o IdentitiesOnly=yes -o StrictHostKeyChecking=yes -o BatchMode=yes -o UserKnownHostsFile=/home/patrick/work/put.gd/work/remote-builders/$HOST/known_hosts \
  "$PACKAGE" "$HERE/proton_accept.py" "$REPO/desktop_lock.py" patrick@${IP[$HOST]}:work/pf65/ || { echo "STOP: copy failed"; exit 4; }
NAME=$(basename "$PACKAGE")
"${SSH[@]}" "cd ~/work/pf65 && if [ ! -d app ]; then case '$NAME' in *.AppImage) mkdir app && chmod 700 '$NAME' && (cd app && ../'$NAME' --appimage-extract >/dev/null) ;; *.deb) mkdir app && dpkg-deb -x '$NAME' app ;; *) echo unsupported package; exit 5 ;; esac; fi; ls -d app/squashfs-root app/usr 2>/dev/null | head -1" > /tmp/pacc-$SESSION.root || { echo "STOP: extract failed"; exit 4; }
ROOT=$(cat /tmp/pacc-$SESSION.root); [ "$ROOT" = app/usr ] && ROOT=app
echo "app root on $HOST: ~/work/pf65/$ROOT"

# 3. The run. Its exit status is 0 only when every case passed.
"${SSH[@]}" "cd ~/work/pf65 && python3 proton_accept.py --app $ROOT --work $RUN --host $HOST --session $SESSION ${EXTRA[*]}"; STATUS=$?
echo "acceptance exit status: $STATUS"

# 4. Results back to the workstation: numbers, logs and local copies of captures. No share links are in them.
mkdir -p "$OUT"
"${SSH[@]}" "cd ~/work/pf65/$RUN && tar -c results.json summary.txt resident.log local-copies profile/state/putgd/logs 2>/dev/null" | tar -x -C "$OUT" 2>/dev/null
echo "results copied to $OUT"; ls "$OUT"

# 5. Nothing of ours left running, then release. A refused release is reported, not forced.
"${SSH[@]}" 'pgrep -a -u $(id -u) putgd | grep -c "work/pf65" || true; ls ~/.local/share/applications 2>/dev/null | grep -c "^putgd.desktop$" || true' | tr '\n' ' '; echo "(our processes left, our desktop entries left)"
lock release $HOST --resource proton --session $SESSION --verified-clean | head -1
lock release $HOST --session $SESSION | head -4
lock status $HOST | grep -q "($SESSION)" && { echo "desktop lock still held: checking again"; lock release $HOST --session $SESSION --verified-clean | head -2; }
exit $STATUS
