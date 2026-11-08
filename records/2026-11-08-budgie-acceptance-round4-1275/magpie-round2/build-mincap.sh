set -e
cd /w/kit; mkdir -p gen; P=/usr/share/wayland-protocols/staging
for x in ext-foreign-toplevel-list ext-image-capture-source ext-image-copy-capture; do
 wayland-scanner client-header $P/$x/$x-v1.xml gen/$x-v1-client-protocol.h
 wayland-scanner private-code $P/$x/$x-v1.xml gen/$x-v1.c
done
gcc -O1 -g -Wall -Igen mincap.c gen/*.c -lwayland-client -o mincap
ls -la mincap
