#!/bin/sh
# full.sh DESKTOP LEADER [extra text_proof.py arguments]: all three triggers with the real helper (issue 1428).
set -eu
cd "$(dirname "$0")"
desktop=$1; leader=$2; shift 2
rm -f region.txt click.txt
exec python3 text_proof.py --desktop "$desktop" --leader "$leader" --host-input ./host_input.py --screen 1920 1080 --region 0 0 1 1 \
  --triggers hotkey tray window --fixture ./fixture.sh --ask-region "$PWD/region.txt" --ask-click "$PWD/click.txt" \
  --raise-window 'put.gd 1428 fixture' --first-light --helper-watch ./helper_watch.py \
  --needle 'synthetic text fixture' --expect '(put\.gd 1428 synthetic text fixture, line \d+\s*)+' "$@"
