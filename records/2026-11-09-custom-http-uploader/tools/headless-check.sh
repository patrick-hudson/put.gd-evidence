#!/bin/sh
# #1361: the three real receivers against a headless private resident of the build under test.
R=$HOME/work/i1361-run5
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
$B/putgd-cli --version-json > $R/build.json
python3 $HOME/work/i1361/tools/lab/http_receivers/check_uploads.py --cli $B/putgd-cli --sxcu-dir $HOME/work/i1361-run4/sxcu "$@" > $R/check.json 2> $R/check.err
echo "check exit=$?"
$B/putgd-cli ui.quit > /dev/null 2>&1
sleep 2
