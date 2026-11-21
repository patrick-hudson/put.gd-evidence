#!/bin/bash
# rpt_ct.sh TAG SRC: bin/replay-TAG = SRC's tracker with fill + cell tracers
set -e
cd ~/work/w1557; [ -d var/$1 ] && mv var/$1 var/$1-prev-$(date +%s); mkdir -p var/$1/src/core
cp $2/src/core/ScrollTracker.cpp $2/src/core/ScrollTracker.h var/$1/src/core/
python3 tools/filltrace.py var/$1/src/core/ScrollTracker.cpp
python3 tools/celltrace.py var/$1/src/core/ScrollTracker.cpp
[ -n "$WHYTRACE" ] && python3 tools/whytrace.py var/$1/src/core/ScrollTracker.cpp
g++ -std=c++20 -O2 -fPIC $(pkg-config --cflags Qt6Gui) -Ivar/$1/src -I$2/src $2/tests/fixtures/scroll_tracker_replay.cpp var/$1/src/core/ScrollTracker.cpp -o bin/replay-$1 $(pkg-config --libs Qt6Gui)
ls -la bin/replay-$1
