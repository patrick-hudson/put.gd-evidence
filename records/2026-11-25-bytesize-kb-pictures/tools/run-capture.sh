#!/bin/sh
# usage: run-capture.sh before|after ATTEMPT [--offscreen]   (every attempt gets a new empty run folder; on m74 under the desktop lock unless --offscreen)
L=$1; J=$HOME/work/c2041
mkdir -p $J/run
exec python3 $J/tools/capture2041.py --build $J/$L/build/dev --run $J/run/$L-$2 --label $L $3
