#!/bin/bash
set -u; cd ~/work/i1187
for r in 1 2; do for b in base775 fix1187; do ./runpair.sh "s-$b" "$b/squashfs-root" "$r" --reclaim-at 110,170; echo "s-$b-b$r" >> out/abab.progress; done; done; echo all-done >> out/abab.progress
