#!/bin/bash
# rpt.sh TAG SRC: replay tool for SRC's tracker with the fill tracer -> ~/work/w1557/bin/replay-TAG (-O2)
set -e
cd ~/work/w1557; mkdir -p bin var/$1/src/core
cp $2/src/core/ScrollTracker.cpp $2/src/core/ScrollTracker.h var/$1/src/core/
python3 tools/filltrace.py var/$1/src/core/ScrollTracker.cpp
CXX="g++ -std=c++20 -O2 -fPIC $(pkg-config --cflags Qt6Gui) -Ivar/$1/src -I$2/src"
$CXX $2/tests/fixtures/scroll_tracker_replay.cpp var/$1/src/core/ScrollTracker.cpp -o bin/replay-$1 $(pkg-config --libs Qt6Gui)
ls -la bin/replay-$1
