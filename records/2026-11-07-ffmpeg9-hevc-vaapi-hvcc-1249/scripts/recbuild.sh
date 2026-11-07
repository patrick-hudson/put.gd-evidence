#!/bin/bash
# usage: recbuild.sh ROOT VARIANT PREFIXTAG... -- configures and builds putgd-record from ROOT/VARIANT against ROOT/prefix-PREFIXTAG into VARIANT/build/ff-PREFIXTAG
set -u
R=$1; V=$2; shift 2
cd $R/$V
for T in "$@"; do
  PKG_CONFIG_PATH=$R/prefix-$T/lib/pkgconfig cmake -S . -B build/ff-$T -G Ninja -DCMAKE_BUILD_TYPE=Debug -DCMAKE_PREFIX_PATH=$PWD/build/sdk -DBUILD_TESTING=OFF > $R/cmake-$V-$T.log 2>&1; c=$?
  cmake --build build/ff-$T --target putgd-record -j10 > $R/build-$V-$T.log 2>&1; b=$?
  v=$(grep -E "^PUTGD_AV_libavformat_VERSION" build/ff-$T/CMakeCache.txt | cut -d= -f2)
  echo "$V $T cmake=$c build=$b libavformat=$v" | tee -a $R/recstatus
done
