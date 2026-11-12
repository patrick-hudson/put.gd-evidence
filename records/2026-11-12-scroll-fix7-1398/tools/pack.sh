#!/bin/sh
# pack.sh OUT PREFIX... : the small files of the named campaigns' runs (results, comparisons, exclusions, helper logs
# without the per-frame lines) as a tar on stdout's file OUT.
cd ~/work/sf7 || exit 1
out=$1; shift
tmp=pack-$$; mkdir $tmp
for p in "$@"; do
  for d in runs/$p-*; do
    [ -d $d ] || continue
    n=$(basename $d); mkdir $tmp/$n
    for f in result.json verification.json exclude.json; do [ -f $d/$f ] && cp $d/$f $tmp/$n/; done
    [ -f $d/helper.log ] && grep -vE "scroll tap buffer|scroll frame:" $d/helper.log > $tmp/$n/helper.log
  done
done
tar -C $tmp -czf $out .
find $tmp -type f -delete; find $tmp -depth -type d -empty -delete
ls -la $out | awk '{print $5}'
