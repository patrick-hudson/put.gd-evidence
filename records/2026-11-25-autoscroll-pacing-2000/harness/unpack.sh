set -euo pipefail
umask 077
cd ~/work/i2000
head=$1; package=$2; dest="pkg-$head"
mkdir "$dest"
(cd "$dest"; rpm2cpio "../$package" | cpio -idm --quiet)
meta=$(find "$dest" -name build-info.json -print)
cmp "$meta" "src-$head/build/release/build-identity/build-info.json"
cat "$meta"
ldd "$dest/usr/bin/putgd-record" | awk '/not found/ {print; miss=1} END {exit miss}'
sha256sum "$package" "$dest/usr/bin/putgd-record"
