#!/bin/sh
# Recording loops with the published nightly: cancel, quit and kill aimed at the Shell's bar placement.
cd ~/work/fx5
rm -f nightly.done nightly.status
for spec in "rpcq 28 0.30,0.35,0.40,0.45,0.50,0.55,0.60" "rpc 28 0.30,0.35,0.40,0.45,0.50,0.55,0.60" "rpk 28 0.30,0.35,0.40,0.45,0.50,0.55,0.60" "rsc 21 0,0.05,0.1" "rsq 10 0.2,0.6"; do
  set -- $spec
  timeout 1500 python3 fx5.py n-$1 $1 $2 --delays $3 --recover > n-$1.console 2>&1
  echo "$1 rc=$?" >> nightly.status
done
echo done > nightly.done
