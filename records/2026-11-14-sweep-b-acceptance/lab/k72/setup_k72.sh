#!/bin/bash
set -eu
cd /home/patrick/work/sb1114
trap 'code=$?; printf "%s\n" "$code" > setup-k72.done' EXIT
sudo -n apt-get -y install /home/patrick/work/sb1114/artifacts/ubuntu26.04/putgd_26.1113.4927~dev+gdd7e9c4b18b7_amd64.deb > install-native.log 2>&1
mkdir -m700 analyzer
image=$(python3 -c 'from pathlib import Path;print(next(Path("artifacts/appimage").glob("*.AppImage")).resolve())')
chmod 700 "$image"
(cd analyzer && "$image" --appimage-extract > extract.log)
