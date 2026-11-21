#!/bin/bash
cd ~/work/b1782/h
NETS="104.153.0.0/16 149.137.0.0/16 206.190.0.0/16"
API=104.153.233.180
B=candidate2
./shape.sh on 640 60 $NETS > c3-shape-on.log 2>&1
python3 run.py $B upload shaped 2 60 > c3-shaped.log 2>&1
( sleep 60; ./stall.sh on $API $NETS > c3-stall-on.log 2>&1 ) &
python3 run.py $B upload stall 1 20 > c3-stall.log 2>&1
wait
./stall.sh off >> c3-stall-on.log 2>&1
./shape.sh show > c3-shape-stats.log 2>&1
./shape.sh off >> c3-shape-stats.log 2>&1
echo CHAIN_DONE >> c3-stall.log
