#!/bin/sh
# usage: run-capture.sh before|after ATTEMPT   (run on d69 under the desktop lock; every attempt gets a new empty run folder)
L=$1; J=$HOME/work/c2035
mkdir -p $J/run
exec python3 $J/tools/capture2035.py --build $J/$L/build/dev --run $J/run/$L-$2 --label $L --rfb $J/tools/rfb.py --vnc-port 5900
