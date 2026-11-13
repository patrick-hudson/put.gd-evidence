set -eu
out="$HOME/work/ocr-integration-bcb-artifacts"
# Preserve the failed dpkg-format attempt, then record a corrected literal-format query.
podman exec -i pg1438-deb-clean sh > "$out/deb-clean-before.tsv" <<'DEB'
set -eu
for p in libtesseract5 liblept5 libzxing3 tesseract-ocr-eng; do
  if dpkg-query -W -f='${db:Status-Abbrev}' "$p" 2>/dev/null | grep -q '^ii'; then exit 1; fi
done
dpkg-query -W -f='${Package}\t${Version}\t${Installed-Size}\n'
DEB
podman inspect pg1438-deb-clean pg1438-rpm-clean pg1438-arch-clean > "$out/clean-container-inspect.json"
printf 'Corrected DEB preflight passed; no OCR runtime or English data packages installed.\n'
