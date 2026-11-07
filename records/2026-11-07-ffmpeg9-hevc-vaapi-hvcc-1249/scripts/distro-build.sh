#!/bin/bash
# usage: distro-build.sh DIR -- builds putgd-record from DIR/putgd-src (and DIR/putgd-unfixed) against the distro FFmpeg; AWSSDK pin relaxed to the builder's 1.11.907 in this scratch copy only
set -u
D=$1
for V in putgd-src putgd-unfixed; do
  cd $D/$V
  cmake -S . -B build/distro -G Ninja -DCMAKE_BUILD_TYPE=Debug -DCMAKE_PREFIX_PATH=$PWD/build/sdk -DBUILD_TESTING=OFF > $D/cmake-$V.log 2>&1; c=$?
  nice cmake --build build/distro --target putgd-record -j4 > $D/build-$V.log 2>&1; b=$?
  echo "$V cmake=$c build=$b libavformat=$(grep -E '^PUTGD_AV_libavformat_VERSION' build/distro/CMakeCache.txt | cut -d= -f2)"
done
