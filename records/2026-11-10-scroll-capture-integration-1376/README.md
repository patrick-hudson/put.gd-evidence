# Scroll capture integration for issue 1376

Integration of the helper and resident halves in `patrick-hudson/put.gd-desktop`. Final source: `bd59f802fb693b8719a89f52e8c61a271a0707a2`, branch `feat/scroll-capture`. The initial full CTest campaign used `253008cc4cfc4071448a082ecf1a9339228de20f`; its three failures were fixed and retested on the final source. No real-desktop acceptance is claimed.

Host: k72, 192.168.68.72, Kubuntu 26.04, GCC 15.2.0, distro dynamically linked Qt 6.10.2, official AWS C++ SDK 1.11.924. Source/build directory: `/home/patrick/work/scroll-integrate-1376`. Both helper-enabled Debug dev and `PUTGD_RECORDING=OFF` application builds passed. The initial configure failure selected the host's older SDK 1.11.907; setup was corrected to the existing 1.11.924 installation under `/home/patrick/work/wd1107/build/`.

## Changes and verification

The resident computes one maxPixels budget from imagePixels, imageBytes/4 and the editor admission limit. It refreshes capability probes, treats their pending states as transient, orders GNOME selection and bar placement/hiding before capture, handles Stop before the first frame as cancellation, and wires the real helper backend when its sibling binary exists. The finished PNG is admitted and routed before staging is removed. Four bar states were added to the catalog.

- Full `ctest --preset dev`: 151/154 passed in 1193.51 seconds. Preserved failures: `edit_operations_integration` returned scroll_unavailable instead of output_required; `gui_tray` expected the old nine-entry menu; `gui_settings_advanced` found a suppressed unavailable-source badge. All three were corrected.
- Targeted post-fix CTest: `edit_operations_integration`, `gui_tray`, `gui_settings_advanced`, `scroll_service_integration`: 4/4 passed in 83.86 seconds. The full suite was not repeated after these corrections.
- The original full run passed `scroll_stitcher_contract`, `scroll_capture_x11` (39.65 seconds), and `scroll_service_integration`, as well as native UI lifecycle and the headless labwc test using the existing labwc 0.9.3 installation.
- Final Python runs: release suites 402 passed with 5 skips; unit suites 98 passed; CI suites 210 passed with 1 skip; MCP 8 passed; config schema 12 passed. An earlier release run had 12 setup errors before Git history was installed in the builder copy; the rerun passed. Earlier logs are retained.
- Reference prototype built and run on k72: 74 passed, 0 failed, 5 documented known limitations. This is reference-algorithm evidence, not desktop acceptance.
- All four catalog bar states rendered and were checked (record-only offscreen catalog; no compositor proof).
- Helper-disabled production smoke: scroll.capabilities returned available=false and recording_helper_missing.

## Real resident and helper CLI run

Private Xvfb `:137`, 1280x900, no window manager/compositor, private session bus, real `putgd` and `putgd-record`, real XTest wheel input into `test_scroll_page_fixture`. It was visible through loopback VNC 5937, workstation tunnel 5993, and the wall entry `Scroll capture 1376 k72 Xvfb`. Runtime `/tmp/sc1376-b835jf_2/r`; its resolved resident socket was 41 UTF-8 bytes, checked before launch. Build manifest and saved visuals are in `e2e/`. The exact scripts are in `reports/`.

The fixture was at root rectangle [100,60,640,600], with 80 bar-coded rows of 40 pixels each. The script triggered scroll.prepare, scroll.start and polled scroll.inspect via the production CLI. It independently decoded every pixel line's sixteen barcode cells, including the fine-line patterns, checking a gap-free prefix and correct row order.

- Full page: operation `c2d13c32-fb6d-4304-a5a5-704c6cced387`, end_of_content, PNG 640x3200, all 80 rows once and in order, present in history as image/png.
- Cap: operation `307872e0-5212-42c6-aab4-6a2609834d93`, height_cap, PNG 640x2000, exact 50-row prefix, present in history. An isolated notification API peer received urgency 2 and `Stopped at 2,000 px. The page continues below.` This proves notification delivery to the API, not a compositor's visible toast.
- Cancel: operation `d7a29009-84fd-4741-929d-fe276170c32e`, cancelled, no history row and no staging files. The fixture accepted no input except the helper's wheel events and pointer motion.

The VNC/root screenshot and capturing screenshots show only the synthetic fixture and the bar outside the captured rectangle. The helper and resident never touched a real bucket or user objects. No credentials or private profiles are included.

## Cleanup and remaining gates

The test script terminated and waited for its resident and fixture. Its wrapper stopped and waited for its exact Xvfb, VNC and notification-peer PIDs. The owned Xvfb and VNC PIDs were verified absent and port 5937 closed. The owned workstation SSH tunnel and wall entry were removed. No physical desktop lock was needed or acquired, and no VM was booted. Host-side evidence and private run state remain preserved.

Not verified: current-build real-desktop acceptance on Cinnamon, GNOME, Plasma, Budgie or Hyprland; the AppImage desktop entry on Plasma 6.7 or earlier. Prior standalone probe records remain separate evidence and do not close those gates.
