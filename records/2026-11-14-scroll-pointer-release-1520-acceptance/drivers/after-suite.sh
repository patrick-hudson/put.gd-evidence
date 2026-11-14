#!/bin/sh
set -eu
cd "$HOME/work/s1520"
set -a; . ./session.env; set +a
export PATH=$HOME/work/s1520/bin:$PATH CLI=$HOME/work/s1520/bin/cli-a VNC=${VNC:-5900} RESUME=870,956 STOP=960,956
for mode in live pointer api cancel stoptop large; do
 python3 campaign.py a "$mode" > "a/$mode-driver.log" 2>&1
done
