#!/bin/sh
# usage: run-capture.sh before|after ATTEMPT [SCENES]   (run on m74 under the desktop lock; every attempt gets a new empty run folder)
L=$1; J=$HOME/work/c2042
mkdir -p $J/run
exec python3 $J/tools/capture2042.py --build $J/$L/build/dev --run $J/run/$L-$2 --label $L --scenes ${3:-history,editor,scroll}
