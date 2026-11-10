#!/bin/sh
# #1361: annotate pictures through put.gd's own editor in a headless private resident.
# usage: annotate-run.sh IN_DIR OUT_DIR SPEC
R=$HOME/work/i1361-run6
B=$HOME/work/i1361/build/dev
mkdir -p $R/cfg $R/data $R/state $R/cache $R/rt && chmod 700 $R $R/rt
export XDG_CONFIG_HOME=$R/cfg XDG_DATA_HOME=$R/data XDG_STATE_HOME=$R/state XDG_CACHE_HOME=$R/cache XDG_RUNTIME_DIR=$R/rt
export QT_QPA_PLATFORM=offscreen
unset DISPLAY WAYLAND_DISPLAY
rm -f $R/rt/putgd/session.sock
setsid dbus-run-session -- sh -c 'exec '$B'/putgd --background' > $R/resident.log 2>&1 < /dev/null &
i=0; while [ ! -S $R/rt/putgd/session.sock ] && [ $i -lt 100 ]; do sleep 0.2; i=$((i+1)); done
[ -S $R/rt/putgd/session.sock ] || { echo "resident did not start"; exit 3; }
sleep 4
python3 $HOME/work/i1361-annotate1361.py --cli $B/putgd-cli --in "$1" --out "$2" --spec "$3"
echo "annotate exit=$?"
$B/putgd-cli ui.quit > /dev/null 2>&1
sleep 2
