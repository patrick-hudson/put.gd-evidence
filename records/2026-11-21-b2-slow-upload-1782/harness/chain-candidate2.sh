#!/bin/bash
# Candidate rows for #1782 on k72. Shaping self-removes after 120 min.
cd ~/work/b1782/h
NETS="104.153.0.0/16 149.137.0.0/16 206.190.0.0/16"
API=104.153.233.180
B=candidate2
./shape.sh on 640 120 $NETS > c-shape-on.log 2>&1
python3 run.py $B upload shaped 2 60 > c-shaped.log 2>&1
# Stall: start a shaped 20 MiB upload, then stall every upload connection after 60 s.
( sleep 60; ./stall.sh on $API $NETS > c-stall-on.log 2>&1 ) &
python3 run.py $B upload stall 1 20 > c-stall.log 2>&1
wait
./stall.sh off >> c-stall-on.log 2>&1
CANCEL_AFTER=120 python3 run.py $B upload cancel 1 60 > c-cancel.log 2>&1
./shape.sh show > c-shape-stats.log 2>&1
./shape.sh off >> c-shape-stats.log 2>&1
python3 run.py $B upload normal 1 60 > c-normal.log 2>&1
python3 run.py $B upload normallarge 1 100 > c-normallarge.log 2>&1
echo CHAIN_DONE >> c-normallarge.log
