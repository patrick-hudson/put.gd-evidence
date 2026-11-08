#!/bin/bash
# No put.gd, no capture client: Magpie plus one foot with WAYLAND_DEBUG, for $SECS s.
# MODE=none|grim-T|grim-o. Prints wl_surface.commit and wl_callback.done per 5 s.
S=$(mktemp -d /w/runs/${TAG:-nocap}-XXXX); echo "$S"
export XDG_RUNTIME_DIR=$(mktemp -d /tmp/rt-XXXX); chmod 700 $XDG_RUNTIME_DIR
export XDG_CONFIG_HOME=$S/config XDG_DATA_HOME=$S/data XDG_STATE_HOME=$S/state XDG_CACHE_HOME=$S/cache S
mkdir -p $XDG_CONFIG_HOME
export SECS=${SECS:-90} MODE=${MODE:-none} GAP=${GAP:-3} FIRST=${FIRST:-5}
dbus-run-session -- bash -c '
 export WAYLAND_DISPLAY=wayland-77
 QT_QPA_PLATFORM=offscreen /w/magpie/b/bin/org.buddiesofbudgie.Magpie-0.0.1 --platform-display-libs mir:virtual --virtual-output 1920x1080 > $S/compositor.log 2>&1 & C=$!
 for i in $(seq 1 50); do [ -S $XDG_RUNTIME_DIR/wayland-77 ] && break; sleep 0.2; done; sleep 2
 WAYLAND_DEBUG=1 foot -a win1 -T win1 -W 60x20 sh -c "while :; do date +%s.%N; sleep 0.05; done" > $S/foot.out 2> $S/foot.wl & F=$!
 T0=$(date +%s.%N); echo $T0 > $S/t0
 sleep 3
 python3 -I /w/src/tools/lab/wayland_toplevels.py > $S/toplevels.json 2>&1
 ID=$(python3 -c "import json,sys;d=json.load(open(sys.argv[1]));print(d[\"ext\"][0][\"identifier\"])" $S/toplevels.json); echo id=$ID > $S/id
 END=$(python3 -c "print($T0+$SECS)")
 sleep $FIRST
 N=0
 while [ "$(python3 -c "import time;print(int(time.time()<$END))")" = 1 ]; do
   if [ "$MODE" = grim-T ]; then N=$((N+1)); grim -T "$ID" $S/cap$N.png 2>> $S/grim.err; echo "$N $(date +%s.%N) rc=$?" >> $S/caps
   elif [ "$MODE" = grim-o ]; then N=$((N+1)); grim $S/cap$N.png 2>> $S/grim.err; echo "$N $(date +%s.%N) rc=$?" >> $S/caps
   fi
   sleep $GAP
 done
 ps -o pid,stat,wchan:20,comm -p $F > $S/foot.ps
 kill $F; wait $F 2>/dev/null; kill $C; wait $C 2>/dev/null'
python3 - "$S" <<'PY'
import re,sys,glob,os,hashlib
from collections import Counter
S=sys.argv[1]
t0=None; c=Counter(); d=Counter(); r=Counter(); last={}
first=None
for l in open(S+'/foot.wl',errors='replace'):
    m=re.match(r'\[\s*(\d+\.\d+)\]',l)
    if not m: continue
    t=float(m.group(1))/1000
    if first is None: first=t
    b=int((t-first)//5)*5
    if ' -> wl_surface' in l and '.commit(' in l: c[b]+=1; last['commit']=t-first
    if 'wl_callback' in l and '.done(' in l: d[b]+=1; last['done']=t-first
    if 'wl_buffer' in l and '.release(' in l: r[b]+=1; last['release']=t-first
print('bucket(s): commits/frame-done/buffer-release')
for b in sorted(set(c)|set(d)|set(r)): print(f'{b:4d}: {c[b]:4d} {d[b]:4d} {r[b]:4d}')
print('last', {k:round(v,1) for k,v in last.items()})
caps=sorted(glob.glob(S+'/cap*.png'),key=lambda p:int(re.search(r'cap(\d+)',p).group(1)))
if caps:
    hs=[hashlib.md5(open(p,'rb').read()).hexdigest()[:6] for p in caps]
    print('captures',len(hs),'distinct consecutive',sum(1 for a,b in zip(hs,hs[1:]) if a!=b)); print(' '.join(hs))
PY
[ -s $S/grim.err ] && sort $S/grim.err | uniq -c | head -5; cat $S/foot.ps 2>/dev/null
