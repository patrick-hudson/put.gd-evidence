set -eu
cd /home/lab/b1364v
chmod +x ./*.AppImage
mkdir -m700 an
cd an
../*.AppImage --appimage-extract > extract.log
cd ..
python3 check_socket_paths.py --socket /run/user/1000/putgd/session.sock > socket-preflight.json
an/squashfs-root/usr/bin/putgd-record --version > build-version.txt
pactl get-default-sink > default-sink.txt
pactl get-default-source > default-source.txt
pactl list short sources > sources-before.txt
labwc --version > labwc-version.txt
budgie-panel --version > budgie-version.txt 2>&1 || true
