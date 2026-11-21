#!/bin/bash
# bt.sh TAG SRC: test_scroll_tracker for SRC (-O2) as bin/tt-TAG
cd ~/work/w1557; mkdir -p bin
g++ -std=c++20 -O2 -Wall -I$2/src -I$2/tests $2/tests/unit/test_scroll_tracker.cpp $2/tests/fixtures/ScrollSynthetic.cpp $2/src/core/ScrollTracker.cpp -o bin/tt-$1 2>&1 | grep -E "error|warning" | head -20
ls -la bin/tt-$1
