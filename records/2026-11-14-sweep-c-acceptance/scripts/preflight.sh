#!/bin/bash
set -eu
cd /home/patrick/work/sc1114
cp /home/patrick/work/w7-34/putgd_26.1113.4926~dev+gff636bba2bee_amd64.deb restore-putgd.deb
sha256sum restore-putgd.deb >restore-package.sha256
dpkg-query -s putgd >original-package.txt
sudo -n apt-get -s install /home/patrick/work/sb1114/artifacts/ubuntu24.04/putgd_26.1113.4927~dev+gdd7e9c4b18b7_amd64.deb >install-preview.log
cat install-preview.log
