#!/bin/sh
# both_run.sh TAG BUILD ANALYZER X1,X2,X3 Y [record_run options...]
# #1363 beside #1364 in one resident session: a delayed desktop capture with its countdown, a monitor recording with
# click highlights and three presses, and a delayed desktop capture again. One summary.
tag=$1; build=$2; analyzer=$3; xs=$4; y=$5; shift 5
LAB=${LAB:-$HOME/work/i1364/src/tools/lab}; RUNS=${RUNS:-$HOME/work/i1364/runs}; mkdir -p $RUNS
x1=${xs%%,*}; rest=${xs#*,}; x2=${rest%%,*}; x3=${rest#*,}
python3 $LAB/record_run.py --run $RUNS/$tag --build pr=$build --analyzer $analyzer --video marker --rounds 1 --no-notifications --keep-unpaired \
  --target monitor --format mp4 --lead 3 --system tone --pause-for 0 --pause-at 14 --after 2 \
  --click 4,$x1,$y,left --click 8,$x2,$y,right --click 12,$x3,$y,middle --frames --delayed-capture desktop:3 "$@" > $RUNS/$tag.out 2>&1
echo "== $tag rc=$? load $(cut -d' ' -f1 /proc/loadavg)"
python3 $LAB/summarize_run.py $RUNS/$tag/results.json
touch $RUNS/$tag.done
