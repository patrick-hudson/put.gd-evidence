# Quick redact follow-up on Cinnamon and Plasma

This physical desktop run covers the PDF IP, wrapped key, empty assignment, split access ID and JSON password cases in PR #1916. m74 ran Linux Mint 22.3 Cinnamon X11 with Xreader, xed and GNOME Terminal. k72 ran Kubuntu 26.04 Plasma Wayland with Okular at Fit Page, Kate and Konsole. The terminal used line-numbered cat output. Both hosts generated identical synthetic text locally.

| Build | Package | Commit | Tree |
| --- | --- | --- | --- |
| Published nightly | `26.1122.6439~nightly` | `28e9f91060cd10a69921268eefc89e2b6fe4a50e` | `65df546861260bcb92f41ce3f24d3130e90e0c11` |
| Candidate | `26.1122.6623~dev+ga3412dc25192` | `a3412dc251929c7f843d71af57478c7fe090cae5` | `27d15f30cd4797e554b40dc04a0cc81d7805cf83` |

Resident diagnostics confirmed both trees on both hosts. Native desktop captures went through the production editor and all five built-in categories. The named PDF IPs were checked visually and by their foreground pixels. The aggregate IP counts use a 98% answer-key box threshold. Text scoring compares saved pixels of each expected value and checks that the empty assignment and inline comment stay readable and unchanged. The timings measure the Quick redact call through its completed reply. put.gd’s offscreen editor annotated each picture. [Candidate CI run](https://github.com/patrick-hudson/put.gd-desktop/actions/runs/45069937742)

## Pass and fail

Each result is nightly → candidate.

| Named PDF case | m74 | k72 |
| --- | --- | --- |
| IPv4 CIDR · page 4 | Fail → Pass | Pass → Pass |
| Bracketed IPv6 with port and CIDR · page 4 | Pass → Pass | Fail → Fail |
| Link-local IPv6 CIDR · page 10 | Pass → Pass | Fail → Fail |
| Link-local IPv6 CIDR · page 16 | Pass → Pass | Fail → Fail |

| Text case | m74 xed | m74 GNOME Terminal | k72 Kate | k72 Konsole |
| --- | --- | --- | --- | --- |
| wrapped base64 | Pass → Pass | Fail → Fail | Fail → Fail | Fail → Fail |
| inline dev comment | Fail → Fail | Fail → Fail | Fail → Fail | Fail → Fail |
| preceding APP_SECRET | Pass → Pass | Pass → Pass | Pass → Pass | Pass → Pass |
| empty DATABASE_URL | Fail → Fail | Fail → Fail | Fail → Fail | Fail → Fail |
| split AKIA ID | Pass → Pass | Pass → Pass | Fail → Fail | Pass → Pass |
| first query password | Fail → Pass | Fail → Pass | Fail → Pass | Fail → Pass |
| spaced JSON password | Fail → Pass | Fail → Pass | Fail → Pass | Fail → Pass |

The candidate covers both JSON passwords on all four surfaces, including the spaced suffix. Some masks also cover adjacent JSON and URL context. The empty assignment improves on Kate and in both terminals, with glyph clipping still measurable. The inline comment stays partly clipped. Kate still misses the split access ID. Its padded continuation regressed from 419 of 792 foreground pixels covered to 224 of 792. Both builds completely cover the two visual lines of the long quoted value there. The terminals leave the padded continuation readable.

Full IP box hits for pages 4, 10 and 16 on m74 were 16 → 18, 15 → 17 and 19 → 21 out of 28 per page. k72 had one full box hit on each page in both builds, with an additional partial on page 4. The k72 IPv4 CIDR glyphs were entirely covered on both builds despite the mask's 90% box overlap. No scored IP moved to a worse coverage grade.

## Annotated pictures

Durations are seconds. Each host's columns link to the saved nightly and candidate images.

| Capture | m74 nightly | m74 candidate | k72 nightly | k72 candidate |
| --- | --- | --- | --- | --- |
| PDF page 4 | [1.21](m74-pdf4-nightly.png) | [1.30](m74-pdf4-candidate.png) | [1.76](k72-pdf4-nightly.png) | [1.78](k72-pdf4-candidate.png) |
| PDF page 10 | [1.29](m74-pdf10-nightly.png) | [1.31](m74-pdf10-candidate.png) | [1.76](k72-pdf10-nightly.png) | [1.74](k72-pdf10-candidate.png) |
| PDF page 16 | [1.41](m74-pdf16-nightly.png) | [1.37](m74-pdf16-candidate.png) | [1.74](k72-pdf16-nightly.png) | [1.76](k72-pdf16-candidate.png) |
| Editor | [1.09](m74-editor-nightly.png) | [1.05](m74-editor-candidate.png) | [0.90](k72-editor-nightly.png) | [0.90](k72-editor-candidate.png) |
| Terminal | [0.93](m74-terminal-nightly.png) | [0.94](m74-terminal-candidate.png) | [1.03](k72-terminal-nightly.png) | [1.04](k72-terminal-candidate.png) |

## Builder restoration

- m74 finished on the published nightly. The clean desktop release receipt is dated 2026-11-22T21:18:00Z.
- k72 finished on the published nightly. The clean desktop release receipt is dated 2026-11-22T21:22:26Z.
