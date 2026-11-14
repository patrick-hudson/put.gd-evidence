#!/bin/bash
# Round 4 on Plasma 6.8.2 (#1515): the optimised build, both browsers, both drivers.
cd ~/work/scroll-session/lab
export LAB_BUILD=release
for kind in chromium firefox; do
  nav=""; [ $kind = firefox ] && nav=1
  LAB_TAG=r4 LAB_NAV_JS=$nav python3 sess.py $kind news user,auto
  LAB_TAG=r4 python3 sess.py $kind github,wiki user,auto
  LAB_TAG=r4 LAB_MAX=30000 python3 sess.py $kind python user,auto
  LAB_TAG=r4-jump LAB_JUMP=1 python3 sess.py $kind wiki user
done
