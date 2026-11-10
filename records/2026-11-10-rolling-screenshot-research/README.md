# Rolling screenshot (auto-scroll capture): research and stitcher prototype

Research for the put.gd-desktop issue "Rolling screenshot: auto-scroll capture on every desktop",
collected on 2026-11-09 against `nightly` at `32a9a763e`. Nothing here is product code or desktop
acceptance evidence. The plan in the issue is the authority; where these notes recommend
something else, the issue wins and says why.

## Contents

| Path | What it is |
| --- | --- |
| `prototype/scroll_stitcher.{h,cpp}` | Offset finder and assembler: row signatures, sticky header and footer detection, offset search, streaming output. C++20, standard library only. |
| `prototype/scroll_session.{h,cpp}` | The auto-scroll control loop behind `IScrollInjector`, `IFrameSource` and `IClock`: settle detection, step planning, end detection, recovery. |
| `prototype/synthetic_app.{h,cpp}`, `prototype/test_main.cpp` | Test only: a seeded synthetic document, a viewport renderer with sticky bands, scrollbar, hover, caret and animation, a fake smooth-scrolling application, and the test suite. |
| `prototype/build.sh` | One `g++` call; `./build.sh asan` for the sanitizer build. |
| `notes/stitcher-prototype.md` | The algorithm as implemented, constants, every test with its result, timing, memory, known limitations, Qt porting notes. |
| `notes/scroll-injection.md` | Scroll injection per desktop (XTest, Mutter RemoteDesktop, Clutter virtual device, KWin fake input, wlr virtual pointer), read from upstream source, and how ShareX stitches. Each claim is tagged verified-in-source, inferred or untested. |
| `notes/codebase-map.md` | Where the feature touches put.gd: capture flow, frame sources, overlays, adapters, agent surface, limits, packaging, tests, docs. |

## Prototype result

```sh
cd prototype
./build.sh
./test_stitcher --no-timing     # 74 passed, 0 failed, 5 known limitations
./test_stitcher                 # adds the timing table
```

The 128-run randomized session sweep reconstructs the document exactly whenever the application
scrolls a constant distance per wheel notch. No offset the stitcher reported as verified was
wrong in any run. The five known limitations are listed in `notes/stitcher-prototype.md`; the
important one is that the matcher assumes rows repeat bit-exactly, which resampled frames
(fractional display scaling) will break. That case is untested.

## Corrections to the notes

- `notes/scroll-injection.md` infers that the KWin desktop-file route cannot work from an
  AppImage. put.gd's `AppRun` already writes a per-mount desktop entry for `putgd-record` on
  Plasma, so the same entry can carry the extra interface.
- The same note recommends the GNOME Shell extension for injection. The plan uses a Mutter
  RemoteDesktop session linked to the screen cast instead and keeps the extension as the fallback.
- `notes/codebase-map.md` recommends a new helper with still grabs. The plan reuses the
  `putgd-record` frame streams instead.
- No code in the notes was run on a desktop. The prototype was run only against its synthetic
  application.
