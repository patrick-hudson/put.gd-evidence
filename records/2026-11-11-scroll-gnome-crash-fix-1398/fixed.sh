#!/bin/sh
# Step 4 loops with the CI RPM of the fix (3b9701cb3): scroll first, then the recording path.
cd ~/work/fx5
rm -f fixed.done fixed.status
date -u +%s > fixed.start; date +"%Y-%m-%d %H:%M:%S" > fixed.start.local
for spec in "pcq 32 0,0,0.02,0.05" "pc 32 0,0,0.02,0.05" "pk 32 0,0,0.02,0.05" "sc 30 0,0.05,0.1" "sq 30 0.2,0.5,1.0" "rpcq 28 0.30,0.35,0.40,0.45,0.50,0.55,0.60" "rpc 28 0.30,0.35,0.40,0.45,0.50,0.55,0.60" "rpk 28 0.30,0.35,0.40,0.45,0.50,0.55,0.60" "rsc 21 0,0.05,0.1"; do
  set -- $spec
  timeout 1500 python3 fx5.py f-$1 $1 $2 --delays $3 --recover > f-$1.console 2>&1
  echo "$1 rc=$?" >> fixed.status
done
echo done > fixed.done
