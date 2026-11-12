#!/bin/sh
# devtext.sh NAME KIND... : the text controls (gtkfull, qtfull) with the dev build of the d69 tree as the resident (lab check before a push).
cd ~/work/sf7 || exit 1
export SF6_P=$PWD SF7=$PWD
DEV=$HOME/work/s1376/src/build/dev
N=$1; shift
touch active
python3 rmowned.py c d s cache r archive > rmowned.log 2>&1
mkdir controls-before-$N
for d in qtfull-00 gtkfull-00; do [ -d $d ] && mv $d controls-before-$N/; done
PATH=$DEV:$PATH python3 - "$@" > $N.console 2>&1 <<'PY'
import os, sys, json, time
from pathlib import Path
import record_run
dev = str(Path.home() / 'work/s1376/src/build/dev')
orig = record_run.session_environment
def patched():
    e, d = orig()
    e['PATH'] = dev + ':' + e.get('PATH', '/usr/bin:/bin')
    return e, d
record_run.session_environment = patched
import pass2 as p
p.setup()
time.sleep(2)
P = p.P
for proc in Path('/proc').iterdir():
    if proc.name.isdigit():
        try:
            if (proc / 'comm').read_text().strip() == 'putgd-ui' and ('XDG_CONFIG_HOME=' + str(P / 'c')).encode() in (proc / 'environ').read_bytes().split(b'\0'):
                os.kill(int(proc.name), 15)
        except OSError:
            pass
time.sleep(1)
print(json.dumps(json.loads((P / 'identity.json').read_text()).get('build')))
print(os.readlink('/proc/%s/exe' % (P / 'resident.pid').read_text().strip()))
for kind in sys.argv[1:]:
    try:
        p.batch(kind, 1)
        r = json.loads((P / (kind + '-00') / 'result.json').read_text())
        c = r.get('capture', {}); res = c.get('result', c)
        print(kind, c.get('state'), res.get('endReason'), res.get('height'), res.get('note'), json.dumps(r.get('verification'))[:200])
    except Exception as e:
        import traceback; print(kind, 'ERROR', traceback.format_exc()[-500:])
PY
kill $(cat resident.pid) 2>/dev/null
sleep 2
rm -f active
echo finished > $N-all.done
