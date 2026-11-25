set -u
cd ~/work/x2064/cand1/src || exit 1
nice cmake --build build/release -j4 --target test_scroll_capture_driver test_scroll_page_fixture > ../build2.log 2>&1 || { echo "build failed"; tail -5 ../build2.log; exit 1; }
cmp build/release/build-identity/build-info.json ~/work/x2064/cand2pkg/usr/share/putgd/build-info.json || { echo "identity mismatch"; exit 1; }
echo IDENTITY-OK
D=$HOME/work/x2064/cand1/src/build/release/test_scroll_capture_driver; H=$HOME/work/x2064/cand2pkg/usr/bin/putgd-record
cd ~/work/x2064/lab
export LAB_X11=1 LAB_DRIVER=$D LAB_HELPER=$H LAB_NOREF=1
{
for seed in 4 5 6; do LAB_PACE=brisk LAB_SEED=$seed LAB_TAG=cand2-b$seed python3 run.py firefox github,stackoverflow user; done
LAB_TAG=cand2 python3 run.py firefox github,wiki auto
cd ~/work/x2064 && python3 x4k.py c2-4k $D $H $HOME/work/x2064/cand1/src/build/release/test_scroll_page_fixture 3840 2160
} > ~/work/x2064/recheck.log 2>&1
grep -h '"name"\|"tag"' ~/work/x2064/recheck.log | cut -c1-260
test -z "$(pgrep -x putgd-record || true)" && echo "no helper left"
