cd ~/work/x2064/lab || exit 1
rm -f ~/work/x2064/arun.done
test -z "$(pgrep -x putgd-record || true)" || { echo "helper running"; exit 1; }
for b in nightly cand1; do
  export LAB_DRIVER=$HOME/work/x2064/f44drv/$b/test_scroll_capture_driver LAB_HELPER=$HOME/work/x2064/ai-$b/squashfs-root/usr/bin/putgd-record LAB_SEED=1 LAB_NOREF=1
  LAB_TAG=$b python3 run.py firefox wiki user,auto
  LAB_TAG=$b python3 run.py firefox github user,auto
done
test -z "$(pgrep -x putgd-record || true)" && echo "no helper left"
echo DONE > ~/work/x2064/arun.done
