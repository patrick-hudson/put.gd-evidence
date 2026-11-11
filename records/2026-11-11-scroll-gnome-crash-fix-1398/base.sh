#!/bin/sh
# Baseline counts with the branch-head RPM: every variant, crashes recovered in place.
cd ~/work/fx5
for v in pcq pc pk sc sq; do
  timeout 1500 python3 fx5.py b-$v $v ${N:-20} --delays ${D:-0,0.05,0.1,0.2} --recover > b-$v.console 2>&1
  echo "$v rc=$?" >> base.status
done
echo done > base.done
