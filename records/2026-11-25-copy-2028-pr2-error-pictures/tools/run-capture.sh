#!/bin/sh
# usage: run-capture.sh before|after ATTEMPT   (run on m74 under the desktop lock; every attempt gets a new empty run folder)
L=$1; J=$HOME/work/c2028
mkdir -p $J/run
exec python3 $J/tools/capture2028.py --build $J/$L/build/dev --run $J/run/$L-$2 --label $L
