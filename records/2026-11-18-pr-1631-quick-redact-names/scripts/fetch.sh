#!/bin/bash
# fetch.sh HOST NAME  -> pulls NAME-orig/red/.json into scratchpad/HOST and verifies
S=/tmp/claude-1000/-home-patrick--t3-worktrees-put-gd-t3-4467dc54-32c1a4eaa1c59795/f11be110-ac15-469f-998e-62c698830fac/scratchpad
h=$1; n=$2; case $h in f44) ip=192.168.68.70;; k72) ip=192.168.68.72;; m74) ip=192.168.68.74;; esac
mkdir -p $S/$h
for f in $n-orig.png $n-red.png $n.json; do $S/cp.sh $h patrick@$ip:work/qr1618/state/out/$f $S/$h/ >/dev/null; done
python3 $S/verify.py $S/$h/$n-orig.png $S/$h/$n-red.png $S/$h/$n.json | tee $S/$h/$n-verify.json | python3 -c "import json,sys;d=json.load(sys.stdin);print('verify pass=',d['pass'],'marks=',d['marksCount'],'outside_changed=',d['changed_outside_marks_px'])"
