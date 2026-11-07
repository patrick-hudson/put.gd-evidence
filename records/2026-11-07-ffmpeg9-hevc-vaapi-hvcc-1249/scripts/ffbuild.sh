#!/bin/bash
# usage: ffbuild.sh ROOT TAG... -- builds each FFmpeg TAG with media.json configure (minus libx264/libx265: not in Fedora) into ROOT/prefix-TAG
set -u
R=$1; shift
mapfile -t CFG < <(python3 -c 'import json,sys; print("\n".join(f for f in json.load(open(sys.argv[1]))["ffmpeg"]["configure"] if f not in ("--enable-libx264","--enable-libx265")))' ~/work/ff9-hevc-fix-tools/media.json)
for T in "$@"; do
  E=$(echo "${CFG[@]}" | sed -E 's/libx264,libx265,//')
  read -r -a C <<< "$E"
  git -C $R/ffmpeg worktree add --detach $R/src-$T $T > $R/wt-$T.log 2>&1 || { echo "$T worktree failed"; continue; }
  mkdir $R/build-$T $R/prefix-$T; cd $R/build-$T; start=$(date +%s)
  $R/src-$T/configure --prefix=$R/prefix-$T --libdir=$R/prefix-$T/lib "${C[@]}" > $R/configure-$T.log 2>&1; c=$?
  make -j$(nproc) > $R/make-$T.log 2>&1; m=$?
  make install > $R/install-$T.log 2>&1; i=$?
  echo "$T configure=$c make=$m install=$i seconds=$(( $(date +%s) - start ))" | tee -a $R/status
done
