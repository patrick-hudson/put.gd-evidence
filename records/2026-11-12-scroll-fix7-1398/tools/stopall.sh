#!/bin/sh
# Stops this harness's campaign on the host: the runner by its process group, then browser and resident by their pids.
cd ~/work/sf7 || exit 1
export SF6_P=$PWD SF7=$PWD
# The runner and what it started, each by its own pid (the runner first, so that it starts nothing more).
for p in $(pgrep -u $(id -u) -x runall.sh); do kill -TERM $p 2>/dev/null; done
ps -u $(id -u) -o pid=,args= | grep -E 'python3 (live7|controls7)[.]py|python3 -c import pass2' | while read p rest; do kill -TERM $p 2>/dev/null; done
sleep 1
[ -e browser.pid ] && kill $(cat browser.pid) 2>/dev/null
[ -e fixture.pid ] && kill $(cat fixture.pid) 2>/dev/null
[ -e resident.pid ] && kill $(cat resident.pid) 2>/dev/null
sleep 3
rm -f active
ps -u $(id -u) -o pid=,args= | grep -E 'python3 (live7|controls7)[.]py' && echo 'still running: a harness script'
for n in firefox firefox-esr chromium putgd putgd-ui putgd-record runall.sh; do pgrep -u $(id -u) -x $n > /dev/null && echo "still running: $n $(pgrep -u $(id -u) -x $n | tr '\n' ' ')"; done
ls -d profile-* 2>/dev/null | while read d; do python3 rmowned.py $d; done
echo stopped
