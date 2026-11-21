#!/bin/bash
# rr.sh TAG RUNDIR [extra replay args]: replay RUNDIR/tee/run0 through bin/replay-TAG into RUNDIR/rr-TAG (fills.txt = fill trace)
cd ~/work/w1557
T=$1; run=$(readlink -f $2); shift 2
o=$run/rr-$T; mkdir -p $o
sed -E "s#^.*/tee/run0/#$run/tee/run0/#" $run/tee/run0/list.txt > $o/list.txt
start=$(date +%s)
FILLTRACE=$o/fills.txt bin/replay-$T --max-height 60000 --list $o/list.txt --out $o "$@" > $o/replay.log 2>&1
echo "rc=$? secs=$(( $(date +%s) - start ))" >> $o/replay.log
