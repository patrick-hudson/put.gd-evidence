# Hyprland per-try results

`commands` counts ordinary pointer commands after first motion; relative corrections are separate. The final `stopped` end reason can come from the explicitly recorded later API Stop, so only `stoppedByClick` counts. Slight negative delays are same-tick millisecond timestamp quantization.

## Candidate: random 1–6 seconds

| Try | Start ms | Pause ms | Commands | Corrections | First click stopped |
|---|---:|---:|---:|---:|---|
| a-random-1 | 2767 | 0.393 | 0 | 0 | True |
| a-random-2 | 1791 | 44.052 | 0 | 0 | True |
| a-random-3 | 1726 | 66.702 | 0 | 0 | True |
| a-random-4 | 2676 | 185.671 | 0 | 0 | True |
| a-random-5 | 2521 | -0.332 | 0 | 0 | True |
| a-random-6 | 3663 | 0.67 | 0 | 0 | True |
| a-random-7 | 4947 | 0.474 | 0 | 0 | True |
| a-random-8 | 1709 | 76.681 | 1 | 0 | False |
| a-random-9 | 5348 | 48.864 | 1 | 0 | True |
| a-random-10 | 5621 | -0.064 | 0 | 0 | True |

## Published nightly: random 1–6 seconds

| Try | Start ms | Pause ms | Commands | Corrections | First click stopped |
|---|---:|---:|---:|---:|---|
| b-random-1 | 2204 | no pause | 25 | 0 | False |
| b-random-2 | 5246 | no pause | 29 | 0 | False |
| b-random-3 | 4673 | no pause | 28 | 0 | False |
| b-random-4 | 1906 | no pause | 13 | 0 | False |
| b-random-5 | 2361 | no pause | 12 | 0 | False |
| b-random-6 | 5784 | no pause | 27 | 0 | False |
| b-random-7 | 5075 | no pause | 12 | 0 | False |
| b-random-8 | 4721 | no pause | 15 | 0 | False |
| b-random-9 | 2110 | no pause | 28 | 0 | False |
| b-random-10 | 3416 | no pause | 30 | 0 | False |

## Matching-delay control

[Raw recheck](b/failure-recheck.jsonl): requested 1.709 s, measured 1.734 s, no pause, 13 later commands, no correction, first click false; lost_track at 720 px.
