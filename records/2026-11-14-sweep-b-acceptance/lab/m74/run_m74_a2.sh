#!/bin/bash
set -eu
cd /home/patrick/work/sb1114
trap 'code=$?; printf "%s\n" "$code" >physical-m74-a2.done' EXIT
SWEEP_EXPECTED_TREE=1148ea1108a4f28a749607cf4a8ee8cbbdd90fc7 python3 physical_b.py --run /tmp/sba2 --build baseline=/home/patrick/work/sa1113/artifacts/appimage/putgd-26.1113.4899-dev+g036a9225e188-x86_64.AppImage --analyzer analyzer/squashfs-root --video still --target monitor --format mp4 --rounds 1 --system off --no-notifications --precheck-wait 4 > physical-m74-a2.log 2>&1
