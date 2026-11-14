# GNOME 50.6 (f44): auto-scroll paused by the mouse, extension 23 and 24

This PR's build (head 0bfc9325f; built on f44), one resident with its own configuration (local save only). Wikipedia "Linux" in a
Firefox 158 of its own (a fresh process per try), region 240,200 1440x820; the Shell put the bar above it at 240,138.
Each try: auto-scroll from the start; after the start time a relative uinput mouse (flat acceleration) goes
from the middle of the screen (one wall-VNC placement) to the bar's Done at about 600 px/s, one event per 10 ms,
and clicks once. "First click" is Done taking effect on that click. Driver: `lab/trial.py`, from #1514's.

## Extension 23, fixed start, 2 s: 10 of 10 first clicks

| Try | Start (ms) | First click | Paused after the first motion (ms) | Pointer motions sent after it | Put back | Seen by | Shell watch |
| --- | --- | --- | --- | --- | --- | --- | --- |
| v23-fixed-1 | 2004 | yes | 9.0 | 0 | 0 | the bar's leave | no |
| v23-fixed-2 | 2005 | yes | 10.6 | 0 | 0 | the bar's leave | no |
| v23-fixed-3 | 2002 | yes | 9.8 | 0 | 0 | the bar's leave | no |
| v23-fixed-4 | 2002 | yes | 10.7 | 0 | 0 | the bar's leave | no |
| v23-fixed-5 | 2005 | yes | 14.9 | 0 | 0 | on the rest surface: moved with nothing sent | no |
| v23-fixed-6 | 2010 | yes | 22.9 | 0 | 0 | on the rest surface: moved with nothing sent | no |
| v23-fixed-7 | 2005 | yes | 2.9 | 0 | 0 | the bar's leave | no |
| v23-fixed-8 | 2003 | yes | 6.9 | 0 | 0 | the bar's leave | no |
| v23-fixed-9 | 2002 | yes | 3.6 | 0 | 0 | the bar's leave | no |
| v23-fixed-10 | 2004 | yes | 1.6 | 0 | 0 | the bar's leave | no |

## Extension 23, random start, 1 to 6 s: 8 of 10 first clicks

| Try | Start (ms) | First click | Paused after the first motion (ms) | Pointer motions sent after it | Put back | Seen by | Shell watch |
| --- | --- | --- | --- | --- | --- | --- | --- |
| v23-random-1 | 5163 | yes | 9.4 | 0 | 0 | the bar's leave | no |
| v23-random-2 | 2562 | yes | 8.0 | 0 | 0 | the bar's leave | no |
| v23-random-3 | 4011 | yes | 22.2 | 0 | 0 | on the rest surface: moved with nothing sent | no |
| v23-random-4 | 2984 | yes | 4.7 | 0 | 0 | the bar's leave | no |
| v23-random-5 | 3996 | yes | 6.3 | 0 | 0 | the bar's leave | no |
| v23-random-6 | 2046 | yes | 3.6 | 0 | 0 | the bar's leave | no |
| v23-random-7 | 1950 | yes | 13.3 | 0 | 0 | on the rest surface: moved with nothing sent | no |
| v23-random-8 | 5351 | **missed** | 129.9 | 2 | 0 | on the rest surface: moved with nothing sent | no |
| v23-random-9 | 4960 | **missed** | - | 9 | 0 | the bar's leave | no |
| v23-random-10 | 3564 | yes | 12.4 | 0 | 0 | the bar's leave | no |

## Extension 24, fixed start, 2 s: 10 of 10 first clicks

| Try | Start (ms) | First click | Paused after the first motion (ms) | Pointer motions sent after it | Put back | Seen by | Shell watch |
| --- | --- | --- | --- | --- | --- | --- | --- |
| v24-fixed-1 | 2002 | yes | 1.9 | 0 | 0 | on the watch: moved with nothing sent | yes |
| v24-fixed-2 | 2002 | yes | 12.7 | 0 | 0 | on the watch: moved with nothing sent | yes |
| v24-fixed-3 | 2007 | yes | 14.2 | 0 | 0 | on the watch: moved with nothing sent | yes |
| v24-fixed-4 | 2005 | yes | 3.1 | 0 | 0 | the bar's leave | yes |
| v24-fixed-5 | 2008 | yes | 22.6 | 0 | 0 | on the watch: moved with nothing sent | yes |
| v24-fixed-6 | 2005 | yes | 15.6 | 0 | 0 | on the rest surface: moved with nothing sent | yes |
| v24-fixed-7 | 2009 | yes | 8.8 | 0 | 0 | on the watch: moved with nothing sent | yes |
| v24-fixed-8 | 2007 | yes | 2.9 | 0 | 0 | the bar's leave | yes |
| v24-fixed-9 | 2004 | yes | 3.4 | 0 | 0 | the bar's leave | yes |
| v24-fixed-10 | 2002 | yes | 9.0 | 0 | 0 | on the watch: moved with nothing sent | yes |

## Extension 24, random start, 1 to 6 s: 10 of 10 first clicks

| Try | Start (ms) | First click | Paused after the first motion (ms) | Pointer motions sent after it | Put back | Seen by | Shell watch |
| --- | --- | --- | --- | --- | --- | --- | --- |
| v24-random-1 | 4397 | yes | 8.0 | 0 | 0 | on the watch: on the watch | yes |
| v24-random-2 | 3218 | yes | 4.3 | 0 | 0 | on the watch: moved with nothing sent | yes |
| v24-random-3 | 4554 | yes | 16.5 | 0 | 0 | on the watch: moved with nothing sent | yes |
| v24-random-4 | 4264 | yes | 11.9 | 0 | 0 | on the rest surface: moved with nothing sent | yes |
| v24-random-5 | 4108 | yes | 4.6 | 0 | 0 | the bar's leave | yes |
| v24-random-6 | 2311 | yes | 6.1 | 0 | 0 | on the watch: on the watch | yes |
| v24-random-7 | 3131 | yes | 2.7 | 0 | 0 | the bar's leave | yes |
| v24-random-8 | 4725 | yes | 6.3 | 0 | 0 | the bar's leave | yes |
| v24-random-9 | 4083 | yes | 13.4 | 0 | 0 | on the watch: moved with nothing sent | yes |
| v24-random-10 | 5875 | yes | 4.3 | 0 | 0 | the bar's leave | yes |

