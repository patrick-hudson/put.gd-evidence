set -eu
out="$HOME/work/ocr-integration-bcb-artifacts"
podman exec -i pg1438-arch-clean bash > "$out/arch-clean-install.log" 2>&1 <<'ARCH'
set -euo pipefail
for p in tesseract tesseract-data-eng zxing-cpp leptonica; do if pacman -Q "$p" >/dev/null 2>&1; then exit 1; fi; done
config=$(mktemp /tmp/pc.XXXXXX)
sed '/^[[:space:]]*NoExtract[[:space:]]*=/d' /etc/pacman.conf > "$config"
# pacman installs required dependencies only; optional dependencies are never selected.
pacman --config "$config" -U --noconfirm /input/integration-arch/*.pkg.tar.zst
pacman -Q > /input/arch-clean-after.txt
pacman -Qi putgd > /input/arch-installed-dependencies.txt
env -i /usr/bin/putgd-ocr --version-json > /input/arch-helper-identity.json
ldd /usr/bin/putgd-ocr > /input/arch-helper-ldd.txt
if grep -q 'not found' /input/arch-helper-ldd.txt; then exit 1; fi
pacman -Qi tesseract tesseract-data-eng zxing-cpp leptonica zint > /input/arch-ocr-package-sizes.txt
cp -a /var/lib/pacman/local /input/arch-installed-package-db
sha256sum /usr/share/tessdata/eng.traineddata > /input/arch-english-data.sha256
test -s /usr/share/doc/putgd/qrcodegen-LICENSE
printf 'PASS: required-dependencies-only install, helper identity, library resolution, English data and MIT notice.\n'
ARCH
