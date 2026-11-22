#!/bin/bash
W=$HOME/work/i1812; B=$W/pkg/after/root; A=$W/pkg/e1815/root; L=usr/lib/x86_64-linux-gnu/putgd
bash $W/harness/acc.sh e1815-k-before $B $L pkg-after-1
bash $W/harness/acc.sh e1815-k-after $A $L e1815-k-before
bash $W/harness/emoji.sh e1815-after $A $A/$L
echo K1815_DONE > $W/k72-1815.done
