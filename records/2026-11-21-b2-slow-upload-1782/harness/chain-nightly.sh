#!/bin/bash
cd ~/work/b1782/h
./shape.sh on 640 50 104.153.0.0/16 149.137.0.0/16 206.190.0.0/16 > shape-on-nightly.log 2>&1
python3 run.py nightly upload shaped 1 60 > nightly-shaped.log 2>&1
./shape.sh show > shape-stats-nightly.log 2>&1
./shape.sh off >> shape-stats-nightly.log 2>&1
echo CHAIN_DONE >> nightly-shaped.log
