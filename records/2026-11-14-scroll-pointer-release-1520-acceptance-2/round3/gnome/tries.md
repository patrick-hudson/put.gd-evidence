# GNOME per-try results

Relative uinput mouse, flat acceleration, 600 px/s, one event per 10 ms. Initial placement uses one tablet event; all subsequent motion is relative. Random launch jitter 0–1 s. `commands` counts ordinary put.gd pointer commands after first motion; corrections are counted separately. Millisecond helper logging can put a same-tick latency slightly below zero. A later API Stop never counts as a successful first click.

## Candidate: fixed

| Try | Start ms | Pause ms | Commands | Corrections | First click stopped |
|---|---:|---:|---:|---:|---|
| a-fixed-1 | 2002 | 50.899 | 2 | 0 | False |
| a-fixed-2 | 2002 | 52.772 | 2 | 0 | False |
| a-fixed-3 | 2002 | 5.515 | 0 | 0 | True |
| a-fixed-4 | 2002 | 0.269 | 0 | 0 | True |
| a-fixed-5 | 2002 | 5.402 | 0 | 0 | True |
| a-fixed-6 | 2002 | 102.413 | 2 | 0 | False |
| a-fixed-7 | 2002 | -0.055 | 0 | 0 | True |
| a-fixed-8 | 2002 | -0.284 | 0 | 0 | True |
| a-fixed-9 | 2002 | 82.434 | 2 | 0 | False |
| a-fixed-10 | 2002 | 0.941 | 0 | 0 | True |

## Candidate: random

| Try | Start ms | Pause ms | Commands | Corrections | First click stopped |
|---|---:|---:|---:|---:|---|
| a-random-1 | 2894 | 16.267 | 0 | 0 | True |
| a-random-2 | 2592 | -0.081 | 0 | 0 | True |
| a-random-3 | 1758 | 8.831 | 0 | 0 | True |
| a-random-4 | 1865 | 0.711 | 0 | 0 | True |
| a-random-5 | 2308 | 2.655 | 0 | 0 | True |
| a-random-6 | 4624 | 10.419 | 0 | 0 | True |
| a-random-7 | 1075 | 6.881 | 0 | 0 | True |
| a-random-8 | 4350 | 92.282 | 2 | 0 | False |
| a-random-9 | 5806 | 3.907 | 0 | 0 | True |
| a-random-10 | 1523 | 3.481 | 0 | 0 | True |

## Published nightly: fixed

| Try | Start ms | Pause ms | Commands | Corrections | First click stopped |
|---|---:|---:|---:|---:|---|
| b-fixed-1 | 2002 | no pause | 18 | 0 | False |
| b-fixed-2 | 2003 | no pause | 18 | 0 | False |
| b-fixed-3 | 2003 | no pause | 75 | 0 | False |
| b-fixed-4 | 2002 | no pause | 18 | 0 | False |
| b-fixed-5 | 2002 | no pause | 18 | 0 | False |
| b-fixed-6 | 2002 | no pause | 18 | 0 | False |
| b-fixed-7 | 2002 | no pause | 78 | 0 | False |
| b-fixed-8 | 2002 | no pause | 78 | 0 | False |
| b-fixed-9 | 2005 | no pause | 18 | 0 | False |
| b-fixed-10 | 2002 | no pause | 18 | 0 | False |

## Published nightly: random

| Try | Start ms | Pause ms | Commands | Corrections | First click stopped |
|---|---:|---:|---:|---:|---|
| b-random-1 | 4312 | no pause | 74 | 0 | False |
| b-random-2 | 3301 | no pause | 77 | 0 | False |
| b-random-3 | 4429 | no pause | 18 | 0 | False |
| b-random-4 | 3381 | no pause | 75 | 0 | False |
| b-random-5 | 4118 | no pause | 18 | 0 | False |
| b-random-6 | 5966 | no pause | 18 | 0 | False |
| b-random-7 | 3532 | no pause | 21 | 0 | False |
| b-random-8 | 4746 | no pause | 78 | 0 | False |
| b-random-9 | 5084 | no pause | 19 | 0 | False |
| b-random-10 | 5632 | no pause | 81 | 0 | False |

## Separate G1 correction probes

These use only relative motion from the bar, without the main driver’s initial center placement. Start time is randomized between 1 and 6 seconds. The purpose is to exercise the relative correction path; they do not replace the G2 trials.

| Try | Start ms | Pause ms | Commands | Corrections | First click stopped |
|---|---:|---:|---:|---:|---|
| g1-random-1 | 1879 | -0.2 | 0 | 0 | True |
| g1-random-2 | 2929 | 100.333 | 63 | 0 | False |
| g1-random-3 | 4392 | 53.022 | 2 | 0 | True |
| g1-random-4 | 2262 | -0.21 | 0 | 0 | True |
| g1-random-5 | 4105 | 3.04 | 0 | 0 | True |
| g1-random-6 | 2512 | 40.646 | 2 | 0 | True |
| g1-random-7 | 2778 | 11.005 | 0 | 0 | True |
| g1-random-8 | 3428 | 1.106 | 0 | 0 | True |
| g1-random-9 | 5197 | 4.091 | 0 | 0 | True |
| g1-random-10 | 4958 | 0.074 | 0 | 0 | True |
| g1-random-11 | 2760 | 3.316 | 0 | 0 | True |
| g1-random-12 | 1084 | 0.488 | 0 | 0 | True |
| g1-random-13 | 5215 | 8.627 | 0 | 0 | True |
| g1-random-14 | 4580 | 91.092 | 2 | 1 | True |
