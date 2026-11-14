set -eu
cd "$HOME/work/s5302"
set -a; . ./session.env; set +a
export XDG_CONFIG_HOME=$HOME/work/s5302/a/config XDG_DATA_HOME=$HOME/work/s5302/a/data XDG_CACHE_HOME=$HOME/work/s5302/a/cache XDG_STATE_HOME=$HOME/work/s5302/a/state
bash s1.sh a
for mode in fixed random; do
 for i in $(seq 1 10); do
  firefox --profile "$HOME/work/s5302/ff" https://en.wikipedia.org/wiki/Linux
  sleep 5
  python3 -c 'import random,time;time.sleep(random.uniform(0,1))'
  if test "$mode" = fixed; then delay=2; jitter=0; else delay=1; jitter=5; fi
  python3 trial.py --local-center --rel --cli "$HOME/work/s5302/bin/cli-a" --rect 470,200,980,720 --stop 960,956 --log "$HOME/work/s5302/a/helper.log" --vnc 5901 --start "$delay" --jitter "$jitter" --label "a-$mode-$i" >> "a/tries-$mode.jsonl" 2>> "a/tries-$mode.err"
 done
done
CLI=$HOME/work/s5302/bin/cli-a VNC=5901 LOCAL_UI=1 RESUME=870,956 python3 campaign.py a pointer > a/pointer-driver.log 2>&1
