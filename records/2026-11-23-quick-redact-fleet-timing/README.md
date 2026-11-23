# Quick redact fleet timing

### f44

| Input | Build | p50 / p95 / max (s) | Recognition / matching | Peak helper RSS (MiB) | Truncated / failed |
|---|---|---:|---:|---:|---:|
| Ordinary (176) | before | 0.651 / 1.040 / 3.706 | 99.08% / 0.92% | 135.3 | 0 / 0 |
| Ordinary (176) | now | 0.662 / 1.056 / 3.744 | 97.22% / 2.78% | 135.1 | 0 / 0 |
| Corpus (100) | before | 0.345 / 0.875 / 1.910 | 99.44% / 0.56% | 130.5 | 0 / 0 |
| Corpus (100) | now | 0.493 / 1.135 / 6.892 | 97.87% / 2.13% | 155.4 | 1 / 0 |
| 4K dense (5 runs) | before | 4.225 / 4.242 / 4.242 | 98.85% / 1.15% | 177.6 | 0 / 0 |
| 4K dense (5 runs) | now | 8.250 / 8.264 / 8.264 | 96.69% / 3.31% | 177.7 | 0 / 0 |
| 4K faint (5 runs) | before | 0.564 / 0.566 / 0.566 | 99.66% / 0.34% | 99.7 | 0 / 0 |
| 4K faint (5 runs) | now | 0.686 / 0.687 / 0.687 | 98.84% / 1.16% | 102.6 | 0 / 0 |

### d69

| Input | Build | p50 / p95 / max (s) | Recognition / matching | Peak helper RSS (MiB) | Truncated / failed |
|---|---|---:|---:|---:|---:|
| Ordinary (176) | before | 0.759 / 1.254 / 4.603 | 99.23% / 0.77% | 133.0 | 0 / 0 |
| Ordinary (176) | now | 0.772 / 1.266 / 4.626 | 97.63% / 2.37% | 132.3 | 0 / 0 |
| Corpus (100) | before | 0.406 / 0.915 / 1.948 | 99.52% / 0.48% | 124.8 | 0 / 0 |
| Corpus (100) | now | 0.585 / 1.534 / 8.724 | 98.30% / 1.70% | 151.0 | 1 / 0 |
| 4K dense (5 runs) | before | 5.271 / 5.315 / 5.315 | 99.09% / 0.91% | 174.9 | 0 / 0 |
| 4K dense (5 runs) | now | 10.258 / 10.291 / 10.291 | 97.34% / 2.66% | 182.1 | 0 / 0 |
| 4K faint (5 runs) | before | 0.635 / 0.644 / 0.644 | 99.71% / 0.29% | 98.2 | 0 / 0 |
| 4K faint (5 runs) | now | 0.752 / 0.766 / 0.766 | 98.97% / 1.03% | 100.9 | 0 / 0 |

### k72

| Input | Build | p50 / p95 / max (s) | Recognition / matching | Peak helper RSS (MiB) | Truncated / failed |
|---|---|---:|---:|---:|---:|
| Ordinary (176) | before | 0.747 / 1.233 / 4.472 | 99.22% / 0.78% | 133.7 | 0 / 0 |
| Ordinary (176) | now | 0.780 / 1.244 / 4.523 | 97.57% / 2.43% | 133.8 | 0 / 0 |
| Corpus (100) | before | 0.406 / 0.863 / 1.878 | 99.51% / 0.49% | 126.9 | 0 / 0 |
| Corpus (100) | now | 0.593 / 1.496 / 8.559 | 98.29% / 1.71% | 152.7 | 1 / 0 |
| 4K dense (5 runs) | before | 5.165 / 5.183 / 5.183 | 99.08% / 0.92% | 176.8 | 0 / 0 |
| 4K dense (5 runs) | now | 10.074 / 10.103 / 10.103 | 97.28% / 2.72% | 185.8 | 0 / 0 |
| 4K faint (5 runs) | before | 0.630 / 0.635 / 0.635 | 99.70% / 0.30% | 99.2 | 0 / 0 |
| 4K faint (5 runs) | now | 0.736 / 0.738 / 0.738 | 98.93% / 1.07% | 102.0 | 0 / 0 |

### m74

| Input | Build | p50 / p95 / max (s) | Recognition / matching | Peak helper RSS (MiB) | Truncated / failed |
|---|---|---:|---:|---:|---:|
| Ordinary (176) | before | 0.780 / 1.273 / 4.613 | 99.12% / 0.88% | 132.2 | 0 / 0 |
| Ordinary (176) | now | 0.804 / 1.299 / 4.734 | 97.40% / 2.60% | 131.4 | 0 / 0 |
| Corpus (100) | before | 0.424 / 0.925 / 2.256 | 99.49% / 0.51% | 125.1 | 0 / 0 |
| Corpus (100) | now | 0.613 / 1.640 / 10.211 | 98.06% / 1.94% | 151.2 | 1 / 0 |
| 4K dense (5 runs) | before | 5.296 / 5.304 / 5.304 | 99.00% / 1.00% | 174.2 | 0 / 0 |
| 4K dense (5 runs) | now | 10.221 / 10.255 / 10.255 | 97.27% / 2.73% | 177.3 | 0 / 0 |
| 4K faint (5 runs) | before | 0.685 / 0.686 / 0.686 | 99.69% / 0.31% | 96.6 | 0 / 0 |
| 4K faint (5 runs) | now | 0.799 / 0.808 / 0.808 | 98.91% / 1.09% | 99.4 | 0 / 0 |

### aurora-amd

| Input | Build | p50 / p95 / max (s) | Recognition / matching | Peak helper RSS (MiB) | Truncated / failed |
|---|---|---:|---:|---:|---:|
| Ordinary (176) | before | 0.292 / 0.511 / 1.742 | 99.17% / 0.83% | 216.4 | 0 / 0 |
| Ordinary (176) | now | 0.295 / 0.512 / 1.766 | 97.95% / 2.05% | 216.5 | 0 / 0 |
| Corpus (100) | before | 0.170 / 0.374 / 0.855 | 99.48% / 0.52% | 190.6 | 0 / 0 |
| Corpus (100) | now | 0.237 / 0.575 / 3.374 | 98.26% / 1.74% | 208.7 | 1 / 0 |
| 4K dense (5 runs) | before | 1.999 / 2.265 / 2.265 | 99.19% / 0.81% | 209.4 | 0 / 0 |
| 4K dense (5 runs) | now | 3.854 / 4.483 / 4.483 | 97.99% / 2.01% | 209.9 | 0 / 0 |
| 4K faint (5 runs) | before | 0.338 / 0.344 / 0.344 | 99.74% / 0.26% | 155.4 | 0 / 0 |
| 4K faint (5 runs) | now | 0.379 / 0.384 / 0.384 | 99.06% / 0.94% | 158.3 | 0 / 0 |

Before used the distribution-specific published helper from nightly 26.1122.6439 (`28e9f91060cd10a69921268eefc89e2b6fe4a50e`) and a matcher compiled from that commit. Now used the helper and matcher built in Release mode from origin/nightly at `17863e12098e1c270ae635567727ecb5d6c811aa`. Mint used the Ubuntu 24.04 DEB. Aurora used its Fedora 45 Toolbx environment. Each host used the same installed English language data for both builds.

The timer covers production TextJob candidate and word recognition, candidate line assignment and production quickRedact::find with email, phone, IP, card and key categories. Recognition includes memfd preparation, helper execution and result handling. Image decoding and benchmark-process startup precede the timer. Stage percentages divide the sum of each stage by summed recognition and matching time. Candidate conversion and line assignment are included in total wall time. The matcher has empty custom sources and uses the standard harness overload. One benchmark process and one helper per capture allow Linux RUSAGE_CHILDREN to report helper peak RSS. Stage, total and RSS values are from successful calls, including any marked truncated.

A quiet lease covered each builder's headless run. Build order alternated per image and across 4K repeats. Medians use the middle value or the mean of the two middle values. p95 uses nearest rank, so it equals the maximum for each five-run 4K fixture. Per-capture corpus results and its private sample mapping are excluded from this record. The corpus sample used Python random.Random(20261122).sample over the sorted 10,000 PNG/JPG paths without looking at labels.

4K inputs were 3840×2160. The dense input was `c4k/term4k-tokens.png` (SHA-256 `c08f07314f71879ecb8040cade60081fe0cd4da1207df339d35801c75aa02c59`). The faint input was the exact m74 V10 PNG retained for #1924 (SHA-256 `98f31cd81a4eae29fa00443c3ac4e192d4b58661c3c1851b2132de96e6602027`). The 176 ordinary captures came from the retained #1428 set in `r1911/c1428`.

Across the four i5 builders, ordinary p95 rose by 11–26 ms. Dense 4K median rose from 4.23–5.30 s to 8.25–10.26 s, and corpus p95 rose from 0.86–0.93 s to 1.14–1.64 s. The same corpus input returned a truncated result on all five current builds. Recognition accounted for 96.69–99.06% of current measured stage time. Peak helper RSS across all current measurements was 216.5 MiB.

The first Fedora harness link failed because an unused TextLayer function referenced EditDocument. The scratch harness was rebuilt with function sections and linker garbage collection on all hosts before measuring. The product tree was untouched.
