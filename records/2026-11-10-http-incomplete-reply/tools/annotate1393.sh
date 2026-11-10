#!/bin/sh
# #1393: annotate through put.gd's own editor in a headless private resident of the same build.
R=$HOME/work/i1393-pic/annotate
B=$HOME/work/i1393/build/dev
mkdir -p $R/cfg $R/data $R/state $R/cache $R/rt && chmod 700 $R $R/rt
export XDG_CONFIG_HOME=$R/cfg XDG_DATA_HOME=$R/data XDG_STATE_HOME=$R/state XDG_CACHE_HOME=$R/cache XDG_RUNTIME_DIR=$R/rt
export QT_QPA_PLATFORM=offscreen
unset DISPLAY WAYLAND_DISPLAY
rm -f $R/rt/putgd/session.sock
setsid dbus-run-session -- sh -c 'exec '$B'/putgd --background' > $R/resident.log 2>&1 < /dev/null &
i=0; while [ ! -S $R/rt/putgd/session.sock ] && [ $i -lt 100 ]; do sleep 0.2; i=$((i+1)); done
[ -S $R/rt/putgd/session.sock ] || { echo "resident did not start"; exit 3; }
sleep 4
python3 $HOME/work/i1393-annotate.py --cli $B/putgd-cli --in $HOME/work/i1393-pic/shots --out $HOME/work/i1393-pic/annotated --spec $HOME/work/i1393-pic/spec.json
echo "annotate exit=$?"
$B/putgd-cli ui.quit > /dev/null 2>&1
sleep 2
