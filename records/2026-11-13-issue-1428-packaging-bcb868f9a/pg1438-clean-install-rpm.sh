set -eu
out="$HOME/work/ocr-integration-bcb-artifacts"
podman exec -i pg1438-rpm-clean sh > "$out/rpm-clean-install.log" 2>&1 <<'RPM'
set -eu
for p in tesseract-libs leptonica zxing-cpp tesseract-langpack-eng; do if rpm -q "$p" >/dev/null 2>&1; then exit 1; fi; done
dnf -y --setopt=install_weak_deps=False install /input/integration-fedora44/*.rpm
rpm -qa --qf '%{NAME}\t%{VERSION}-%{RELEASE}\t%{SIZE}\n' > /input/rpm-clean-after.tsv
rpm -q --requires putgd > /input/rpm-installed-requires.txt
rpm -q --recommends putgd > /input/rpm-installed-recommends.txt
env -i /usr/bin/putgd-ocr --version-json > /input/rpm-helper-identity.json
ldd /usr/bin/putgd-ocr > /input/rpm-helper-ldd.txt
if grep -q 'not found' /input/rpm-helper-ldd.txt; then exit 1; fi
rpm -q --qf '%{NAME}\t%{VERSION}-%{RELEASE}\t%{SIZE}\n' tesseract-libs leptonica zxing-cpp tesseract-langpack-eng > /input/rpm-ocr-package-sizes.tsv
data=$(rpm -ql tesseract-langpack-eng | sed -n '/\/eng\.traineddata$/p')
test -s "$data"
sha256sum "$data" > /input/rpm-english-data.sha256
rpm -ql putgd | sed -n '/qrcodegen-LICENSE/p' | while IFS= read -r file; do test -s "$file"; done
printf 'PASS: weak-dependencies-disabled install, helper identity, library resolution and English data.\n'
RPM
