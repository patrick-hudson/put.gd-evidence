#!/bin/sh
# verifyall.sh PREFIX : the comparisons of a campaign's runs, after the desktop was given back.
cd ~/work/sf7 || exit 1
for d in runs/$1-*; do
  [ -f $d/capture.png ] && [ -f $d/reference.png ] && [ ! -f $d/verification.json ] && nice python3 live7.py verify $d > $d/verify.log 2>&1
done
echo finished > $1-verify.done
