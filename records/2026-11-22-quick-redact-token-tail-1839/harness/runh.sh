# usage: runh.sh NAME BIN  (on aurora)
set -e
cd /var/home/patrick/work/r1840
n=$1;b=$2;shift 2;mkdir -p runs/$n
d=$(mktemp -d /tmp/r40XXXX)
toolbox run -c putgd-build env TMPDIR=$d ./bin/$b --helper ./src/build/dev/putgd-ocr --data /var/home/patrick/work/pgfix/app/squashfs-root/usr/share/putgd/tessdata --sizes 9,10,11,12,13,14,16,18,20,24,32 --fonts "Adwaita Mono,Adwaita Sans,Cantarell,Liberation Mono,Liberation Sans,Liberation Serif,Noto Sans,Noto Sans Mono,Noto Serif,Red Hat Display,Red Hat Text,Source Code Pro" "$@" > runs/$n/out.json 2>runs/$n/err.txt
echo done > runs/$n/done
