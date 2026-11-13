set -eu
out="$HOME/work/ocr-integration-bcb-artifacts"
podman exec -i pg1438-deb-clean sh > "$out/deb-clean-install.log" 2>&1 <<'DEB'
set -eu
for p in libtesseract5 liblept5 libzxing3 tesseract-ocr-eng; do
  if dpkg-query -W -f='${db:Status-Abbrev}' "$p" 2>/dev/null | grep -q '^ii'; then exit 1; fi
done
apt-get install -y --no-install-recommends /input/integration-ubuntu24.04/*.deb
dpkg-query -W -f='${Package}\t${Version}\t${Installed-Size}\n' > /input/deb-clean-after.tsv
dpkg-query -W -f='${Depends}\n${Recommends}\n' putgd > /input/deb-installed-dependencies.txt
env -i /usr/bin/putgd-ocr --version-json > /input/deb-helper-identity.json
ldd /usr/bin/putgd-ocr > /input/deb-helper-ldd.txt
if grep -q 'not found' /input/deb-helper-ldd.txt; then exit 1; fi
for p in libtesseract5 liblept5 libzxing3 tesseract-ocr-eng; do dpkg-query -W -f='${db:Status-Abbrev}\t${Package}\t${Version}\t${Installed-Size}\n' "$p"; done > /input/deb-ocr-package-sizes.tsv
data=$(dpkg -L tesseract-ocr-eng | sed -n '/\/eng\.traineddata$/p')
test -s "$data"
sha256sum "$data" > /input/deb-english-data.sha256
grep -q 'Nayuki' /usr/share/doc/putgd/copyright
printf 'PASS: no-Recommends install, helper identity, library resolution, English data and retained MIT notice.\n'
DEB
