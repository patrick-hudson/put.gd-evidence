#!/bin/bash
set -eu
cd /home/patrick/work/sb1114
trap 'code=$?; printf "%s\n" "$code" >physical-m74-7.done' EXIT
python3 physical_b.py --run /tmp/sbm7 --build candidate=/home/patrick/work/sb1114/native-bin --analyzer analyzer/squashfs-root --video still --target monitor --format mp4 --rounds 1 --system off --no-notifications --precheck-wait 15 > physical-m74-7.log 2>&1
