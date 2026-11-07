#!/bin/bash
# usage: ffbuild-nonv.sh ROOT TAG... -- like ffbuild.sh, reusing src-TAG, plus --disable-ffnvcodec --disable-nvenc (Fedora's nv-codec-headers 13.1 is too new for these tags); prefix-TAG-nonv
set -u
R=$1; shift
mapfile -t CFG < <(python3 -c 'import json,sys; print("\n".join(f for f in json.load(open(sys.argv[1]))["ffmpeg"]["configure"] if f not in ("--enable-libx264","--enable-libx265","--enable-ffnvcodec","--enable-nvenc")))' ~/work/ff9-hevc-fix-tools/media.json)
for T in "$@"; do
  E=$(echo "${CFG[@]}" | sed -E 's/libx264,libx265,//; s/h264_nvenc,hevc_nvenc,//')
  read -r -a C <<< "$E"
  mkdir $R/build-$T-nonv $R/prefix-$T-nonv; cd $R/build-$T-nonv; start=$(date +%s)
  $R/src-$T/configure --prefix=$R/prefix-$T-nonv --libdir=$R/prefix-$T-nonv/lib "${C[@]}" --disable-ffnvcodec --disable-nvenc > $R/configure-$T-nonv.log 2>&1; c=$?
  make -j$(nproc) > $R/make-$T-nonv.log 2>&1; m=$?
  make install > $R/install-$T-nonv.log 2>&1; i=$?
  echo "$T-nonv configure=$c make=$m install=$i seconds=$(( $(date +%s) - start ))" | tee -a $R/status
done
