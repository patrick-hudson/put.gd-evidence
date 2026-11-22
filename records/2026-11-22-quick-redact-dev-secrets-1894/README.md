# Quick redact developer secrets on Cinnamon and Plasma

Physical desktop acceptance for put.gd #1894, #1895 and #1897 on 2026-11-22. Each builder ran the published nightly first and the candidate second. Both used the same synthetic browser, PDF, terminal and editor inputs. The editor opened each fixture from a native desktop capture. Quick redact ran with email, phone, IP, card and key enabled, and the resulting images were saved locally through the production editor.

| Build | Package version | Commit | Source tree |
| --- | --- | --- | --- |
| Published nightly | `26.1122.6439~nightly` | `28e9f91060cd10a69921268eefc89e2b6fe4a50e` | `65df546861260bcb92f41ce3f24d3130e90e0c11` |
| Candidate | `26.1122.6567~dev+g0c5e0a076ae1` | `0c5e0a076ae1f8de5bfeaf4a2df304db5591f74a` | `c07f246ca8b9fc2f3727d4af4ad6007e4be2c824` |

The physical m74 builder ran Cinnamon on X11 with the Ubuntu 24.04 DEB. The physical k72 builder ran Plasma on Wayland with the Ubuntu 26.04 DEB. Native package artifacts came from the published nightly and candidate CI run 45061689932. The nightly downloads passed the release checksum check. On both hosts, the resident confirmed the expected tree through `putgd-cli diagnostics` before each run. [Published nightly](https://github.com/patrick-hudson/put.gd-desktop/releases/tag/v26.1122.6439-nightly) · [Candidate CI run](https://github.com/patrick-hudson/put.gd-desktop/actions/runs/45061689932)

The table measures elapsed time from sending `editor.apply` through the reply confirming the suggestions were added. Each duration is a single native run under the host’s quiet lease. Pixel checks compare the original and saved copy and verify that each reported mask is solid black. PDF answer-key boxes were mapped into the captured page. Results also account for visible text outside a secret, including PDF label cells, line numbers, variable labels and DevTools source links. A row fails if sensitive text remains readable or ordinary text is obscured. The annotation pictures use the saved outputs and were cropped and marked using put.gd’s own editor in an isolated offscreen session.

## Results

| Host | Fixture | Nightly status and seconds | Candidate status and seconds | Pictures |
| --- | --- | --- | --- | --- |
| m74 | Firefox dark editor | Fail · 2.34 s · 23 masks | Fail · 2.42 s · 27 masks | [nightly](m74-browser-nightly.png) · [candidate](m74-browser-candidate.png) |
| m74 | PDF page 2 | Fail · 0.95 s · 5 masks | Fail · 0.98 s · 4 masks | [nightly](m74-pdf2-nightly.png) · [candidate](m74-pdf2-candidate.png) |
| m74 | PDF page 6 | Fail · 1.04 s · 9 masks | Fail · 1.21 s · 1 masks | [nightly](m74-pdf6-nightly.png) · [candidate](m74-pdf6-candidate.png) |
| m74 | Native terminal | Fail · 0.84 s · 9 masks | Fail · 0.84 s · 9 masks | [nightly](m74-terminal-nightly.png) · [candidate](m74-terminal-candidate.png) |
| m74 | Editor .env | Fail · 1.19 s · 9 masks | Fail · 1.20 s · 10 masks | [nightly](m74-editor-env-nightly.png) · [candidate](m74-editor-env-candidate.png) |
| m74 | Editor database.yml | Fail · 0.92 s · 2 masks | Fail · 0.90 s · 4 masks | [nightly](m74-editor-yml-nightly.png) · [candidate](m74-editor-yml-candidate.png) |
| m74 | Firefox DevTools | Fail · 1.05 s · 4 masks | Fail · 1.07 s · 2 masks | [nightly](m74-devtools-nightly.png) · [candidate](m74-devtools-candidate.png) |
| k72 | Firefox dark editor | Fail · 1.65 s · 23 masks | Fail · 1.76 s · 24 masks | [nightly](k72-browser-nightly.png) · [candidate](k72-browser-candidate.png) |
| k72 | PDF page 2 | Fail · 2.26 s · 32 masks | Fail · 2.94 s · 33 masks | [nightly](k72-pdf2-nightly.png) · [candidate](k72-pdf2-candidate.png) |
| k72 | PDF page 6 | Fail · 1.36 s · 5 masks | Fail · 1.45 s · 1 masks | [nightly](k72-pdf6-nightly.png) · [candidate](k72-pdf6-candidate.png) |
| k72 | Native terminal | Fail · 0.93 s · 9 masks | Fail · 0.94 s · 9 masks | [nightly](k72-terminal-nightly.png) · [candidate](k72-terminal-candidate.png) |
| k72 | Editor .env | Fail · 0.86 s · 9 masks | Fail · 0.88 s · 9 masks | [nightly](k72-editor-env-nightly.png) · [candidate](k72-editor-env-candidate.png) |
| k72 | Editor database.yml | Fail · 0.92 s · 2 masks | Fail · 0.78 s · 3 masks | [nightly](k72-editor-yml-nightly.png) · [candidate](k72-editor-yml-candidate.png) |
| k72 | Firefox DevTools | Fail · 1.35 s · 3 masks | Fail · 1.39 s · 2 masks | [nightly](k72-devtools-nightly.png) · [candidate](k72-devtools-candidate.png) |

The PDF rows use the full-page captures. m74 used Xreader’s automatic full-page scale. k72 used Okular’s Fit Page setting after the first Fit Width capture clipped lower rows. The full-page captures were rerun nightly first and candidate second. Figure labels describe observed changes. The findings below include the remaining misses and over-covers.

### Mint 22.3 · Cinnamon X11

- **Firefox dark editor.** Nightly left the bare database password, MongoDB userinfo, YAML password and Slack webhook visible. The candidate covered those four values. The Sentry DSN userinfo remains visible while the candidate covers the assignment and URL prefix. Matching probably stopped at the scheme delimiter. Both builds cover environment variable labels and some line numbers, the authorization header scaffolding and ordinary DSN text alongside the values. The OCR groups the assignment or URL into a single span. LOG_LEVEL and PORT remain readable.
- **Xreader page 2.** On both builds, 22 answer-key entries were uncovered and one was partial. The partial entry was the wrapped JWT. The 22 were both AWS entries, GitHub classic PAT, GitLab PAT, Stripe, Slack bot, OpenAI, Anthropic, Google, npm, SendGrid, Twilio, Hugging Face, Shopify, DigitalOcean, PostgreSQL and its private IP, MongoDB, Azure connection string, RSA PEM, Slack webhook and fine-grained GitHub PAT. The 708 px-wide document rendered many glyphs only about 7 to 10 px high on dark backgrounds. Recognition is the likely cause of the broad miss. The JWT fragments were likely split in recognition or matching.
- **Xreader page 6.** Nightly covered the Git SHA, SHA-256, ISBN, date/time, ZIP and the harmless invoice digits. It also covered the Git SHA, SHA-256 and ISBN label cells. The candidate leaves all of those entries and labels visible except the invoice digits. The surviving mark is classified as a card, so it is a matching false positive.
- **GNOME Terminal.** Both builds cover the environment values. The candidate restores the database password row’s line number. It still covers several other line numbers and variable names, consistent with grouped OCR spans. LOG_LEVEL and PORT stay visible.
- **xed environment.** Both builds cover the environment values. The candidate also hides the Sentry assignment label that nightly left partly readable. Recognized assignment spans account for the over-cover on that row and several other variable labels. LOG_LEVEL and PORT stay visible.
- **xed database YAML.** The candidate covers the MongoDB userinfo and YAML password that nightly leaves visible. The URL marks also cover ordinary scheme and host text, consistent with matching the entire URL span. The standalone password field label stays readable.
- **Firefox DevTools.** Both builds cover the synthetic bearer and PostgreSQL password. The candidate preserves the two source links that nightly marks. The authorization label and ordinary PostgreSQL scheme and host are still covered because their spans include the secret.

### Kubuntu 26.04 · Plasma Wayland

- **Firefox dark editor.** The candidate covers PostgreSQL and MongoDB userinfo, the YAML password and the Slack webhook, which nightly leaves visible. The AWS access key ID remains visible on both builds, likely from recognition. The Sentry DSN remained exposed on the candidate after nightly covered it. The changed decision suggests matching. The candidate preserves LOG_LEVEL and PORT, which nightly covers. Several environment labels and line numbers, the authorization header context and ordinary URL text remain obscured alongside their secrets.
- **Okular page 2.** At Fit Page, the nightly covers 11 answer-key entries, partially covers 5 and misses 7. The candidate covers 14 entries completely, partially covers 7 and misses 2. The candidate covers database userinfo and the private IP, and covers the Slack webhook path while leaving its scheme prefix visible. The Google API key and the small-font Azure connection string remain readable. The Stripe tail, Anthropic fragments, Shopify top edge, JWT fragments, RSA PEM fragments and faint GitHub PAT are partially exposed. The Anthropic box has more exposed area on the candidate. Recognition is a likely cause for the Google, Azure and faint PAT misses. The narrow end fragments and the multiline JWT and PEM gaps are consistent with recognition spans or matching boundaries. Several variable labels, line numbers and ordinary DSN text are covered with their values.
- **Okular page 6.** Nightly covers the Git SHA and its label, date/time and ZIP. The candidate preserves the label, date/time and ZIP, and still covers the Git SHA value. It is reported as a key match. The 19 other decoy values stay visible.
- **Konsole.** Both builds cover the environment values. The candidate restores the database password row’s line number. Other line numbers and variable names still disappear with their values, consistent with OCR span grouping. LOG_LEVEL and PORT stay visible.
- **Kate environment.** The candidate preserves the database password row’s line number and the editor’s minimap. It hides the Sentry assignment label alongside its already covered value. Other variable labels and line numbers remain over-covered because they share recognized spans with values. LOG_LEVEL and PORT stay visible.
- **Kate database YAML.** The candidate covers the standalone password and more of the PostgreSQL URL. MongoDB userinfo remains partially exposed, with a mark extending down from the preceding row. Recognition or row geometry likely kept it from being recognized as a separate URL. PostgreSQL and Redis masks obscure ordinary URL text, and the Redis mask clips the top of the next line.
- **Firefox DevTools.** The candidate covers the PostgreSQL password prefix left visible by nightly and preserves the bearer source link. Both secrets are covered. The authorization label and the ordinary PostgreSQL scheme and host remain covered because their spans include the secret.

## Builder restoration

- m74 started on `26.1122.6373~dev+gaa202c7a634c` and finished on `26.1122.6439~nightly`. The desktop lease released at 2026-11-22T20:07:13Z. Its purpose records the Sr Manager’s approved transition to the published nightly. The only item recorded as `notMine` was that package. The check had no items left, removed, preexisting or unmatched. Receipt note. “2 process(es) outside the desktop session (no DISPLAY or WAYLAND_DISPLAY; shared SSH work): 313646 313651”
- k72 started on `26.1122.6374~dev+gffeead0fc1f3` and finished on `26.1122.6439~nightly`. The desktop lease released at 2026-11-22T20:13:31Z. Its purpose records the Sr Manager’s approved transition to the published nightly. The only item recorded as `notMine` was that package. The check had no items left, removed, preexisting or unmatched. The receipt contains no notes.
