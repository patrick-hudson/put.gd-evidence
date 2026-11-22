# acc46.sh DIR DEB TREE LEADER LABEL [sensitive]   (on the desktop host)
set -u
d=$1; deb=$2; tree=$3; leader=$4; label=$5; sens=${6:-}
sudo -n dpkg -i "$deb" 2>&1 | tail -1
cd "$d" && setsid -f python3 driver.py "$d" --leader "$leader" --vnc 5900 --tree "$tree" > driver.log 2>&1 < /dev/null
sleep 4; timeout 180 python3 dc.py "$d/c.sock" '["start"]' | head -c 150; echo
for leg in "$label" ${sens:+"$label-up --sensitive"}; do
 for try in 1 2; do timeout 600 python3 leg.py "$d" "$d/fx" $leg > out/leg.txt 2>&1 && break; tail -1 out/leg.txt; done
done
for n in "$label-saved" ${sens:+"$label-up-upload0"}; do
 python3 check.py fx out/$n.png > out/$n-check.json && python3 -c "
import json,sys;s=json.load(open(sys.argv[1]))['summary'];print(sys.argv[2],'showing:',[w for w in s['matchedWordsWithInkShowing'] if 'columns' in w],'touched:',[w for w in s['neighbourWordsTouched'] if 'columns' in w])" out/$n-check.json $n
done
timeout 60 python3 dc.py "$d/c.sock" '["exit"]' >/dev/null; sleep 3
