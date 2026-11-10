#!/bin/sh
# #1361 fix round: the three real receivers through a headless private resident of the merged
# build, then the dark catalog with the surface map and secret-control pin checks.
R=$HOME/work/i1361-run6
B=$HOME/work/i1361/build/dev
mkdir -p $R/cfg $R/data $R/state $R/cache $R/rt && chmod 700 $R $R/rt
(
export XDG_CONFIG_HOME=$R/cfg XDG_DATA_HOME=$R/data XDG_STATE_HOME=$R/state XDG_CACHE_HOME=$R/cache XDG_RUNTIME_DIR=$R/rt
export QT_QPA_PLATFORM=offscreen
unset DISPLAY WAYLAND_DISPLAY
rm -f $R/rt/putgd/session.sock
setsid dbus-run-session -- sh -c 'exec '$B'/putgd --background' > $R/resident.log 2>&1 < /dev/null &
i=0; while [ ! -S $R/rt/putgd/session.sock ] && [ $i -lt 100 ]; do sleep 0.2; i=$((i+1)); done
[ -S $R/rt/putgd/session.sock ] || { echo "resident did not start"; exit 3; }
sleep 4
$B/putgd-cli --version-json > $R/build.json
python3 $HOME/work/i1361/tools/lab/http_receivers/check_uploads.py --cli $B/putgd-cli --sxcu-dir $R/sxcu --allow-insecure-http > $R/check.json 2> $R/check.err
echo "receivers check exit=$?"
$B/putgd-cli ui.quit > /dev/null 2>&1
sleep 2
)
cd $HOME/work/i1361
mkdir -p $R/catalog
python3 tools/ci/check_catalog_render.py --catalog build/dev/putgd-ui-catalog --scheme dark --output $R/catalog/dark > $R/catalog.log 2>&1
echo "catalog render exit=$?"
python3 tools/lab/surface_map/surface_map.py check --catalog $R/catalog/dark > $R/surface-map.log 2>&1
echo "surface map exit=$?"
python3 -m tools.lab.surface_driver.gate check-catalog $R/catalog/dark > $R/pin.log 2>&1
echo "pin check exit=$?"
tail -2 $R/surface-map.log $R/pin.log
