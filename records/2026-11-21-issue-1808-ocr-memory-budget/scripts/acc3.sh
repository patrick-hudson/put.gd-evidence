#!/bin/bash
# acc3.sh : aurora, the corpus through each AppImage's own resident and helper: nightly 6060 (before), candidate (after), both again.
cd ~/work/r1805; H=$(cat host)
M=corpus/records/2026-11-13-issue-1428-corpus-index/manifest.json
one(){ L=$1; D=$HOME/work/i1808/$2/squashfs-root; R=$HOME/work/i1808/res-$L; O=runs/$H/$L
  [ -f $O/summary.json ] && return
  CLI=$HOME/work/i1808/cli-$2.sh; printf '#!/bin/sh\nLD_LIBRARY_PATH=%s/usr/lib:%s/usr/lib/putgd exec %s/usr/bin/putgd-cli "$@"\n' $D $D $D > $CLI; chmod +x $CLI
  python3 -I $HOME/work/i1808/fileocr.py start $R $CLI $D/AppRun --background > $O.start 2>&1
  REF=""; [ -f runs/$H/i1808-appimg-before/rows.json ] && REF="--reference runs/$H/i1808-appimg-before"
  { date -u +%FT%TZ; uptime; } > $O.load
  python3 -I tools/bench.py $M --label $L --out $O $REF -- python3 -I $HOME/work/i1808/fileocr.py recognize $R $CLI {image} > $O.log 2>&1
  uptime >> $O.load
  python3 -I $HOME/work/i1808/fileocr.py stop $R $CLI >> $O.start 2>&1; sleep 3; }
one i1808-appimg-before appimage-nightly6060
one i1808-appimg-after appimage-609c8a6
one i1808-appimg-before2 appimage-nightly6060
one i1808-appimg-after2 appimage-609c8a6
echo ACC3_DONE > runs/$H/i1808-appimg.done
