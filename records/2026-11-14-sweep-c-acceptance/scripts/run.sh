#!/bin/bash
set -eu
cd /home/patrick/work/sc1114
trap 'code=$?; printf "%s\n" "$code" >run-c1.done' EXIT
python3 acceptance_c.py --run /tmp/scc1 --build candidate=/home/patrick/work/sc1114/native-bin --analyzer /home/patrick/work/sb1114/analyzer/squashfs-root --video still --target monitor --format mp4 --rounds 1 --system off --no-notifications --precheck-wait 4 >run-c1.log 2>&1
