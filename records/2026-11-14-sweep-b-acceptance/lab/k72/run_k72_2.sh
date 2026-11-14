#!/bin/bash
set -eu
cd /home/patrick/work/sb1114
trap 'code=$?; printf "%s\n" "$code" >physical-k72-2.done' EXIT
python3 physical_b.py --run /tmp/sbk2 --build candidate=/usr/bin --analyzer analyzer/squashfs-root --video still --target monitor --format mp4 --rounds 1 --system off --no-notifications --precheck-wait 4 > physical-k72-2.log 2>&1
