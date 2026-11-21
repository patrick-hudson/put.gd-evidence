#!/bin/bash
# dense.sh HOSTLABEL CLI RES [BEFORE_DRIVER...] : dense 24 MP page, 3 runs through the packaged resident (and the before helper when given).
cd ~/work/i1808; I=$HOME/work/i1808/synth/dense24.png; CLI=$2; R=$3; shift 3
for i in 1 2 3; do python3 -I fileocr.py recognize $R $CLI $I | python3 -c "import json,sys;d=json.loads(sys.stdin.read());t=d.pop('text','');d['chars']=len(t);print('after',json.dumps(d))"; done
if [ $# -gt 0 ]; then for i in 1 2 3; do QT_QPA_PLATFORM=offscreen "$@" $I | python3 -c "import json,sys;d=json.loads([l for l in sys.stdin if l.startswith('{')][-1]);t=d.pop('text','');d['chars']=len(t);print('before',json.dumps({k:d.get(k) for k in ('totalMs','peakRssKiB','truncated','chars','error')}))"; done; fi
