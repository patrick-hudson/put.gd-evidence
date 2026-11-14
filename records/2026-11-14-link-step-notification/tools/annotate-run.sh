#!/bin/sh
# Annotate the two frames with put.gd's own editor in a private headless resident of this build.
R=$HOME/work/sweep-w8/harness/an
B=$HOME/work/sweep-w8/src/build/dev
mkdir -p $R/cfg $R/data $R/state $R/cache $R/rt $R/in $R/out && chmod 700 $R $R/rt
cp $HOME/work/sweep-w8/harness/out-before/frame.png $R/in/before.png
cp $HOME/work/sweep-w8/harness/out-after/frame.png $R/in/after.png
export XDG_CONFIG_HOME=$R/cfg XDG_DATA_HOME=$R/data XDG_STATE_HOME=$R/state XDG_CACHE_HOME=$R/cache XDG_RUNTIME_DIR=$R/rt
export QT_QPA_PLATFORM=offscreen
unset DISPLAY WAYLAND_DISPLAY DBUS_SESSION_BUS_ADDRESS
setsid dbus-run-session -- sh -c 'exec '$B'/putgd --background' > $R/resident.log 2>&1 < /dev/null &
i=0; while [ ! -S $R/rt/putgd/session.sock ] && [ $i -lt 100 ]; do sleep 0.2; i=$((i+1)); done
[ -S $R/rt/putgd/session.sock ] || { echo "resident did not start"; exit 3; }
sleep 4
python3 $HOME/work/sweep-w8/harness/annotate.py --cli $B/putgd-cli --in $R/in --out $R/out --spec $HOME/work/sweep-w8/harness/spec.json
echo "annotate exit=$?"
$B/putgd-cli ui.quit > /dev/null 2>&1
sleep 2
