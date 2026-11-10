#!/bin/sh
# shot.sh RUN HEAD NAME: QMP screendump of a head, saved as /tmp/p1363-shots/RUN-NAME.png on the VM host.
mkdir -p /tmp/p1363-shots
cd $HOME/work/i1363
python3 tools/lab/lab.py screenshot --run work/lab-runs/$1 --head $2 > /dev/null 2>&1
python3 -c "
import sys
from PIL import Image
Image.open(sys.argv[1]).save(sys.argv[2])" work/lab-runs/$1/witness-head$2.ppm /tmp/p1363-shots/$1-$3.png && echo /tmp/p1363-shots/$1-$3.png
