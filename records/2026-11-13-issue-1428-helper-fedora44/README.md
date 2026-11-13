# Issue 1428 current helper quality on Fedora44

Actual integration helper and test_ocr_run built Release on f44, using the pinned official SDK and distro Qt/Tesseract5.5.4. Build ID, helper/runner hashes, linked libraries, language-data hashes, all 174 input hashes, phase timings/peaks and results are recorded. This is method-development measurement, not candidate acceptance. Each image runs in a new runner process with the real temporary helper, through TextJob; Tesseract CLI is not used.

The corpus is all six original 29-image records. 4K follow-up images are being collected separately and are not included in these 174 scores. Classes and >=11px/<11px bands remain separate; body bar2%, small5%, exact URLs/emails90%. Several bars are exceeded, including terminals, local pages and code. All174 invocations measured without helper errors; truncation and banded flags are retained. The engine worker must settle its method on these numbers before acceptance.

Follow-up: complete-176 combines these174 results with the two new real4K monitor results in helper-scores-fedora44-4k. Build/helper/runner and language-data identities were checked equal before aggregation. The original174 table remains; complete-176/table.md is the complete current corpus table. No engine build or class is pooled with another.

Final single-pass run: full176/ is one invocation of the guarded scorer over all176 images, including engine-library and scorer hashes. full176-table.md is the complete current per-class table. German: german/ uses --language deu and the signature-verified privately extracted Fedora language RPM in german-rpm-identity.json; the14px German prose measures0.117% CER. No system package transaction was performed. All are development measurements, not candidate acceptance.
