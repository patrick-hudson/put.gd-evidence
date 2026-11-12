#!/bin/bash
# One host's proof run, in order. $1 host (m74|d69), $2 package path.
set -u
H=$1; PKG=$2; S=$HOME/work/sopus/s; L=$HOME/work/sopus/l
cd $S
echo "== install $(date -u +%T)"; python3 install-native.py $H $PKG || exit 1
echo "== setup $(date -u +%T)"; python3 pass2.py setup || exit 1
echo "== fixtures $(date -u +%T)"; python3 opus_cases.py nonfixed counter
echo "== controls $(date -u +%T)"; python3 controls7.py ruler text browser sticky resize minimap
echo "== stop resident $(date -u +%T)"; python3 stop_resident.py
echo "== done fixtures $(date -u +%T)"; touch $S/fixtures.done
