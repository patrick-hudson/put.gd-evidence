#!/bin/bash
# Optimised lab build (release preset) of the helper and the lab driver, for timings.
cd /var/home/patrick/work/scroll-session/repo
toolbox run --container putgd-build bash -c "cd /var/home/patrick/work/scroll-session/repo && { [ -f build/release/build.ninja ] || cmake --preset release -DBUILD_TESTING=ON; } && cmake --build build/release --target putgd-record test_scroll_capture_driver test_scroll_page_fixture -j10" > ../build-rel.log 2>&1
echo "done $?" > ../build-rel.done
