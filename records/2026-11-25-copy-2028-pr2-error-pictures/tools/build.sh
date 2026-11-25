set -e
cd ~/work/c2028
for d in after before; do
  (cd $d && cmake --preset dev > ../cfg-$d.log 2>&1 && echo "cfg $d ok")
done
T="putgd putgd-ui putgd-cli putgd-http-worker putgd-clipboard-keeper putgd-capture"
(cd after && nice -n 10 cmake --build --preset dev -j2 --target $T > ../build-after.log 2>&1; echo "after rc=$?") &
(cd before && nice -n 10 cmake --build --preset dev -j2 --target $T > ../build-before.log 2>&1; echo "before rc=$?") &
wait
