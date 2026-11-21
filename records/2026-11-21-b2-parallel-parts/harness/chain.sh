#!/bin/bash
# #1792 candidate rows on d69: shaped (parts outlast a 60 s request timeout on 4 lanes),
# stall mid-part, cancel, then one small single upload unshaped. Shaping self-removes after 60 min.
cd ~/work/b1792/h
B=${1:-cand1}
NETS="104.153.0.0/16 149.137.0.0/16 206.190.0.0/16"
API=$(python3 b2acc.py api)
echo "api $API" > $B-chain.log
python3 run.py $B configure '{"requestTimeoutMs": 60000}' >> $B-chain.log 2>&1
./shape.sh on 4000 60 $NETS > $B-shape-on.log 2>&1
python3 run.py $B upload shaped 1 80 > $B-shaped.log 2>&1
( sleep 45; ./stall.sh on $API $NETS > $B-stall-on.log 2>&1 ) &
python3 run.py $B upload stall 1 80 > $B-stall.log 2>&1
wait
./stall.sh off >> $B-stall-on.log 2>&1
CANCEL_AFTER=45 python3 run.py $B upload cancel 1 80 > $B-cancel.log 2>&1
./shape.sh show > $B-shape-stats.log 2>&1
./shape.sh off >> $B-shape-stats.log 2>&1
python3 run.py $B configure >> $B-chain.log 2>&1
python3 run.py $B upload small 1 10 > $B-small.log 2>&1
echo CHAIN_DONE >> $B-chain.log
