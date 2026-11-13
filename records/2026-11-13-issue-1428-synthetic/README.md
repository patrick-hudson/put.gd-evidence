# Issue 1428 synthetic fixtures

Generated on m74 with distro Pillow and zint 2.13.0 from the included generator.py (SHA-256 in sha256.json). All names, tokens, cards and code payloads are synthetic, never issued credentials or real people.

Includes 24 redact pages in four fonts at 11/14/20 px, light/dark; explicit confusion fixtures and their normalized expectations; clean prose/code and German prose; hash runs; hidden/hostile text; exact/over-24MP, very-wide, no-blank-row and tall-column limits; QR 1–10/40 at 3/5 pixels/module plus version40 at 16 pixels/module, rotated/dark variants, Micro QR, Data Matrix, Aztec, URL/Wi-Fi/contact/plain/binary/hostile payloads, and multiple codes over a busy page with placement ground truth.

Text truth uses Unicode code-point arrays (decode with chr); code payloads use hex. This represents intentionally fake token shapes without triggering GitHub push protection on plain-text Slack fixtures. The original rejected publish is preserved privately. Image bytes are unchanged by that representation.

These are generated inputs, not feature acceptance or a substitute for real-target captures. Per-item/line boxes and font file hashes are in truth JSON. Limit truth is separate from prose scoring. A plain-payload smoke test for each of the four formats was decoded byte-exactly with Debian ZXingReader; exhaustive decode and independent zbar verification remain outstanding. Redaction coverage, result sanitation, and limits/bands await the feature.
