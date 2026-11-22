#!/bin/bash
# emoji.sh LABEL ROOT LIBDIRS : the #1748 round-2 region crops through a packaged resident's own helper, 3 times each.
W=$HOME/work/i1812; L=$1; ROOT=$2; LIB=$3; R=$W/res-$L; CLI=$W/cli-$L.sh; O=$W/emoji-$L.jsonl
printf '#!/bin/sh\nLD_LIBRARY_PATH=%s exec %s/usr/bin/putgd-cli "$@"\n' "$LIB" $ROOT > $CLI; chmod +x $CLI
mkdir -p $R; : > $O
LD_LIBRARY_PATH=$LIB python3 -I $W/harness/fileocr.py start $R $CLI $ROOT/usr/bin/putgd --background > $W/emoji-$L.start 2>&1
for r in 1 2 3; do for I in $W/emoji1748/*.png; do
  python3 -I $W/harness/fileocr.py recognize $R $CLI $I | python3 -c "
import json,sys
d=json.loads(sys.stdin.read()); t=d.get('text','')
em=[c for c in t if ord(c)>=0x1F000 or 0x2600<=ord(c)<=0x27BF]
print(json.dumps({'image':'$(basename $I)','run':$r,'text':t,'emoji':''.join(em),'totalMs':d.get('totalMs'),'peakKiB':d.get('peakKiB'),'error':d.get('error')},ensure_ascii=False))" >> $O
done; done
python3 -I $W/harness/fileocr.py stop $R $CLI >> $W/emoji-$L.start 2>&1
echo EMOJI_DONE >> $W/emoji-$L.start
