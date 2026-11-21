#!/bin/bash
# rpt_old.sh: replay tool for the re-check's tracker (54c5281ac) with the old fill tracer -> bin/replay-old
set -e
cd ~/work/w1557; mkdir -p bin var/old/src/core var/old/tests/fixtures
tar xf old.tar -C var/old --strip-components=1
python3 tools/filltrace_old.py var/old/src/core/ScrollTracker.cpp
g++ -std=c++20 -O2 -fPIC $(pkg-config --cflags Qt6Gui) -Ivar/old/src var/old/tests/fixtures/scroll_tracker_replay.cpp var/old/src/core/ScrollTracker.cpp -o bin/replay-old $(pkg-config --libs Qt6Gui)
ls -la bin/replay-old
