#!/bin/sh
# usage: run-capture.sh before|after   (run on m74 under the desktop lock: desktop_lock.py run m74 --owner copy-2040 --session copy-2040-pics ... -- sh run-capture.sh before)
J=$HOME/work/c2040
exec python3 $J/tools/capture2040.py --build $J/$1/build/dev --run $J/run/$1-1 --label $1
