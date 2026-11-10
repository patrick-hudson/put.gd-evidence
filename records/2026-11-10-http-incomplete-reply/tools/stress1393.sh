#!/bin/sh
# #1393: the fixed tree under contention. First the one case, many times; then the whole
# suite through the builder stress lane. usage: stress1393.sh CASE_RUNS SUITE_ITERATIONS COMMIT
cd $HOME/work/i1393 || exit 2
OUT=$HOME/work/i1393-stress
mkdir -p $OUT
sh $HOME/work/i1393-repro.sh "$1" 8 $OUT/case-fixed aReplyCutOffAfterItsStatusLineIsUnknown 3 > $OUT/case-fixed.txt 2>&1
tail -1 $OUT/case-fixed.txt
python3 tools/ci/stress_suite.py --source $HOME/work/i1393 --out $OUT/suite-fixed --iterations "$2" --hogs 8 --time-scale 3 --commit "$3" \
    --label "http_uploader_integration at $3" -- --preset dev -R http_uploader_integration > $OUT/suite-fixed.txt 2>&1
echo "stress exit=$?"
tail -12 $OUT/suite-fixed.txt
