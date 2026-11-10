# Microphone in recordings and click highlights (#1364)

Evidence for pull request #1372 (code) and #1374 (docs) of put.gd-desktop: the
recording bar's microphone toggle and meter, the device setting, a recording
that survives its microphone being unplugged, and click rings on six desktops.

No real microphone was recorded. Every microphone here is a simulated one made
by `tools/lab/virtual_mic.py` (a null sink remapped into a source), fed with
`record_run.py`'s marker bursts, and removed by its module ids after each run.
Every recording is of the lab's own cover (magenta, with a marker video) and
every clip stayed on its host; this record holds pictures and numbers only.

## Builds

All builds are this pull request's own CI packages, installed on the desktop
they were tested on. Each picture names its build in its caption.

| Build | Commit | What it added over the one before |
| --- | --- | --- |
| 26.1110.4436 | f1bdc4752 | the feature as first complete |
| 26.1110.4437 | 69ad2c6ee | the microphone is no longer the X11 pipeline's clock (a clip that stopped where the microphone was unplugged) |
| 26.1110.4459 | 7e8b3a2e1 | the Click highlights row of Desktop support details shows its whole text and the window-recording limit |
| 26.1110.4465 | 8806fd580 | `progress.clickHighlightsError` stays in `recording.inspect` |
| 26.1110.4480 | 598648cc7 | the ready bar follows microphones that come and go; `recording.audio` |

Nothing between 4436 and 4465 changes the recording bar, the Settings page or
how a ring is drawn, so the bar and ring pictures taken on 4436 stand.

## Desktops

| Desktop | Machine | Sound server |
| --- | --- | --- |
| Cinnamon 6.6.9, X11 | Linux Mint 22.3, physical | PipeWire 1.0.5, WirePlumber 0.4.17 |
| GNOME Shell 50.6, Wayland | Fedora 44, physical | PipeWire 1.6.9, WirePlumber 0.5.18 |
| KDE Plasma 6.3.6, Wayland | Debian 13, physical | PipeWire 1.4.2, WirePlumber 0.5.8 |
| KDE Plasma 6.6.6, Wayland | Kubuntu 26.04, physical | PipeWire 1.6.2, WirePlumber 0.5.13 |
| Hyprland 0.56.2, Wayland | Omarchy guest (QEMU, software rendering) | PipeWire 1.6.9, WirePlumber 0.5.18 |
| Budgie 10.10.3 on labwc 0.20.2, Wayland | Fedora 45 guest (QEMU, software rendering) | PipeWire 1.6.9, WirePlumber 0.5.18 |

## Pictures

| File | What it shows |
| --- | --- |
| `bar-states-catalog.png` | The bar's five microphone states, rendered by `putgd-ui-catalog` |
| `bar-cinnamon.png`, `bar-gnome.png`, `bar-kde63.png`, `bar-kde66.png`, `bar-hyprland.png`, `bar-budgie.png` | The real bar on each desktop: microphone off, on with its meter, and no microphone connected |
| `settings-recording-catalog.png` | Settings, Capture, Screen recording in the catalog: the device choice, click highlights, and the state without a microphone |
| `settings-microphone-cinnamon.png` | The same page on a real desktop: the device list, and the reason no microphone is available |
| `click-rings.png` | One ring per desktop, cut from a frame of the recorded clip, with the measured place and time; window recordings on Cinnamon, GNOME and Hyprland |
| `support-details-catalog.png`, `support-details-kde.png`, `support-details-budgie.png` | Desktop support details: the Click highlights row before and after it showed its whole text, and the window-recording limit on Plasma and Budgie |
| `budgie-cursor.png` | Budgie: the cursor labwc paints beside the one put.gd draws when click highlights are on |
| `alignment-chart.png` | Audio minus video for every marker flash of a microphone-only recording, MP4 and WebM, per desktop |
| `unplug-clip-length.png` | Seconds of clip kept when the microphone is unplugged mid-recording, before and after the clock fix |
| `bar-ready-follow-kde63.png`, `bar-ready-follow-cinnamon.png` | The bar at Ready while a microphone is plugged in, switched on, pulled and plugged in again (build 4480) |
| `output-removed-clip-length.png` | Seconds of clip kept when the output system audio is recorded from is removed mid-recording, and what the recorder read afterwards |

## Numbers

`results/` holds the `results.json` of each `tools/lab/record_run.py` run the
pictures and the pull request's table are made from, named
`<host>-<run>.json`: hosts `m74` (Cinnamon), `f44` (GNOME), `d69` (Plasma
6.3), `k72` (Plasma 6.6), `h65` (Hyprland guest), `b64` (Budgie guest). Runs:
`clicks`, `region`, `window`, `noclicks` (click highlights off), `align`
(microphone alone, MP4 and WebM), `mix` (microphone and system audio across a
pause), `muted` (the simulated microphone plays, the toggle is off), `leak`
(unplugged 6 s in while another output plays a tone), `default` (the system
default input), and on Budgie `nohw` (labwc started with
`WLR_NO_HARDWARE_CURSORS=1`) and `region-on` / `region-off` (the frames of
`budgie-cursor.png`). `m74-cD-leak.json` is the unplug run on 4436, before the
clock fix. Added with build 4480: `d69-kR2.json` and `m74-cR1.json` (`--mic
late`: the microphone plugged in, switched on, pulled and plugged in again at
Ready, then recorded; `readyFollow` holds the steps), and the output-removal
runs `m74-cO-fallback.json`, `m74-cO2-none.json`, `m74-cO2-mic.json`,
`d69-kO-fallback.json` and `d69-kO-mic.json` (`--output-gone-at 6`, with
another output to move to, with none, and with a microphone as the default
input).

Ring times are measured from the pointer's own arrival in the same clip; a
ring's place is the distance of its centre from the press. On Plasma the ring
is KWin's own effect, which adds the button's name beside it: the measured
centre of what appears is about 41 px to the right of the press.
