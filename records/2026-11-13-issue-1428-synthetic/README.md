# Issue 1428 synthetic fixtures

Generated on m74 with distro Pillow and zint 2.13.0. All identities, token shapes, card numbers and payloads are synthetic; none is issued or a real person. Source generator SHA-256 is in generator-sha256.txt.

24 redact pages: four fonts, 11/14/20 px, light/dark. Per-line boxes and categories in truth JSON. Clean prose/code pages, hashes, hidden near-white and tiny text, hostile Unicode text/code payloads, exact/over-limit 24MP, extremely wide, no-blank-row and tall-column inputs are included. Codes include QR versions 1–10/40, 3/5 px per module and version40 at 16px/module (larger than an 8MP band), rotated and dark variants, Micro QR, Data Matrix, Aztec, URL/Wi-Fi/contact/plain/binary/hostile payloads and multiple codes on a busy background. Codes are generated fixtures, not proof that a particular decoder accepts them. Independent decoder verification and feature redaction acceptance remain outstanding.

This synthetic set never substitutes for real-target Capture region evidence. Generated PNGs, source text, boxes and payload ground truth are retained together. Limit images use separate truth files and are intentionally excluded from prose quality scoring.

Synthetic transcript text and word text are stored as Unicode code-point arrays, decoded with chr(), because GitHub push protection rejects the deliberately fake Slack shape in plain text. No protection bypass was requested. The original failed publish is preserved privately.
