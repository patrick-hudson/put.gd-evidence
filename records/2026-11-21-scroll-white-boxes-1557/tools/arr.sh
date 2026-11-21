#!/bin/bash
# arr.sh TAG RUNDIR: aurora variant of rr.sh (replay in the putgd-build toolbox, env passed explicitly)
cd ~/work/w1557
T=$1; run=$(readlink -f $2); shift 2
o=$run/rr-$T; mkdir -p $o
sed -E "s#^.*/tee/run0/#$run/tee/run0/#" $run/tee/run0/list.txt > $o/list.txt
start=$(date +%s)
toolbox run -c putgd-build env FILLTRACE=$o/fills.txt bin/replay-$T --max-height 60000 --list $o/list.txt --out $o "$@" > $o/replay.log 2>&1
echo "rc=$? secs=$(( $(date +%s) - start ))" >> $o/replay.log
