#!/bin/sh
# Annotate with put.gd's own editor in a private headless resident of the installed nightly (/usr/bin).
J=$HOME/work/r1735; B=/usr/bin; R=$J/run/annotate-7171
mkdir -p $R/cfg $R/data $R/state $R/cache $R/rt && chmod 700 $R $R/rt
export XDG_CONFIG_HOME=$R/cfg XDG_DATA_HOME=$R/data XDG_STATE_HOME=$R/state XDG_CACHE_HOME=$R/cache XDG_RUNTIME_DIR=$R/rt
export QT_QPA_PLATFORM=offscreen
unset DISPLAY WAYLAND_DISPLAY DBUS_SESSION_BUS_ADDRESS
setsid dbus-run-session -- sh -c 'exec '$B'/putgd --background' > $R/resident.log 2>&1 < /dev/null &
i=0; while [ ! -S $R/rt/putgd/session.sock ] && [ $i -lt 100 ]; do sleep 0.2; i=$((i+1)); done
[ -S $R/rt/putgd/session.sock ] || { echo "resident did not start"; exit 3; }
sleep 4
python3 $J/tools/annotate1735.py --cli $B/putgd-cli --in $J/crops-7171 --out $J/annotated-7171 --spec $J/spec-7171.json
echo "annotate exit=$?"
$B/putgd-cli ui.quit > /dev/null 2>&1
sleep 2
