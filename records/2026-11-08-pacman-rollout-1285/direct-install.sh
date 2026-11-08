#!/bin/bash
set -euxo pipefail
curl -fsS https://pkg.put.gd/keys/putgd-nightly.asc -o /tmp/putgd-nightly.asc
fingerprint=$(gpg --show-keys --with-colons /tmp/putgd-nightly.asc | awk -F: '$1 == "fpr" {print $10;exit}')
test "$fingerprint" = 4032E28D893BAF66F4AC23D9A11D38D55536B371
pacman-key --add /tmp/putgd-nightly.asc
pacman-key --lsign-key "$fingerprint"
test ! -e /etc/pacman.d/putgd.conf
printf '[putgd-nightly]\nSigLevel = PackageRequired DatabaseRequired\nServer = https://pkg.put.gd/pacman/x86_64/nightly\n' > /etc/pacman.d/putgd.conf
printf '\nInclude = /etc/pacman.d/putgd.conf\n' >> /etc/pacman.conf
pacman -Syu --noconfirm putgd
pacman -Qkk putgd
pacman -Qi putgd
cat /etc/pacman.d/putgd.conf
export XDG_RUNTIME_DIR=/tmp/p1285/r XDG_CONFIG_HOME=/tmp/p1285/config XDG_DATA_HOME=/tmp/p1285/data
putgd-cli --version | tee /tmp/installed-version.txt
grep -F 26.1108.4139-nightly /tmp/installed-version.txt
pacman -R --noconfirm putgd
! pacman -Q putgd
! test -e /usr/bin/putgd-cli
test -f /etc/pacman.d/putgd.conf
printf 'PASS direct CDN repository install/version/uninstall; repository config retained as designed\n'
