#!/bin/sh
# annotate-all.sh DIR: draws every DIR/spec/NAME.json on DIR/pre/NAME.png with put.gd's editor in guest c63 (run on m74).
dir=$1; mkdir -p $dir/out
for spec in $dir/spec/*.json; do
  name=$(basename $spec .json)
  python3 /tmp/p1363-annotate.py c63 $HOME/work/put.gd/work/lab-bootstrap-m74/identity $dir/pre/$name.png $dir/out/$name.png $spec 2>&1 | tail -1
done
