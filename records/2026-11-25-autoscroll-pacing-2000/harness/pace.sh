cd ~/work/i2000
for r in "$@"; do
  echo "$r: steps=$(grep -c "scroll step:" $r/helper.log) notches=[$(grep -o "scroll step: [0-9-]* notches" $r/helper.log | awk '{print $3}' | sort -n | uniq -c | awk '{printf "%sx%s ",$1,$2}')] pxPerNotch=$(grep -o '"pixelsPerNotch":[0-9.]*' $r/driver.log | tail -1) first-measured-at=$(grep -n -o '"pixelsPerNotch":[1-9][0-9.]*' $r/driver.log | head -1) secs=$(python3 -c "import json;print(json.load(open('$r/result.json'))['seconds'])")"
done
