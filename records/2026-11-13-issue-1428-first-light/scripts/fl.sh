#!/bin/sh
# fl.sh DESKTOP LEADER [extra text_proof.py arguments]: first light of the real helper on this desktop (issue 1428).
set -eu
cd "$(dirname "$0")"
desktop=$1; leader=$2; shift 2
rm -f region.txt
exec python3 text_proof.py --desktop "$desktop" --leader "$leader" --host-input ./host_input.py --screen 1920 1080 --region 0 0 1 1 \
  --triggers hotkey --fixture ./fixture.sh --ask-region "$PWD/region.txt" --first-light --helper-watch ./helper_watch.py \
  --needle 'synthetic text fixture' --expect '(put\.gd 1428 synthetic text fixture, line \d+\s*)+' "$@"
