# Editor preview redaction and Qt 6.11 selector startup fixes

Baseline production source: nightly cdac6e4b3174b59e0292b2a16af9abdd110e7514.
Fix A: PR1378, 80ee533971e8aaa07063764abfb55043a6c88ba1, Part of #1377.
Fix B: PR1380, 04ee694dd2523652c06cc8f78560f1bd92e81981, Part of #1379.

## Build and test identities

All compilation and tests ran on f44, Fedora44, kernel7.2.11-200.fc44.x86_64,
GCC16.2.1, distro Qt6.11.2-3.fc44. Source was exported with git archive into
/home/patrick/work/pg-small. The baseline production files were unchanged; the
new A GUI regression and temporary picture-driver CMake targets were added to
that tree. Exported scratch executables report an unknown development version;
the exact source commits above and executable SHA256s in pg-binary-identities.txt
identify the builds. The capture helper uses only Fix B; editor/picture targets
use only Fix A. No workstation builds or tests ran.

The shared SDK was1.11.907, incompatible with the required1.11.924. A separate
official pinned SDK was provisioned under this scratch tree with
bash tools/ci/provision-linux-sdk.sh. Initial configure failures and their
corrections are preserved: use build/sdk/lib (not the old Fedora prefix's lib64)
for PUTGD_AWS_RUNTIME_DIR. Normal configure/build/test presets were used.

## Observed results

- Plain nightly: capture_preparation_x11 FAIL,45 pass/1 fail. The accessibility
  case observes1 connection before mapping where0 is required.
- Minimal Qt program: QApplication plus QCoreApplication::exec alone does not
  connect. Destroying a temporary QWindow triggers the gdb stack in
  tools/pg-min-trace2.log: QWindow::~QWindow -> QAccessible::isActive ->
  QXcbIntegration::accessibility -> QSpiAccessibleBridge -> connectA11yBus.
  Qt6.11.2's destructor has this call; Qt6.10.2's does not. This is not an f44
  accessibility-settings fault. The helper's exec deferral still avoids its
  original root-object trigger, but the new destructor path bypassed it.
- Fix B: unchanged full capture_preparation_x11 PASS9.12s; focused strict
  accessibility case PASS157ms (zero before map, positive after map).
- A regression on unchanged nightly:15 pass/3 fail including83%; it changes
  only covered source colours and compares every rendered widget pixel.
- Fix A: all16 fractional rows PASS (83%,29%,51%,67%, each alone and with blur,
  pixelate, highlight); editor_contract PASS9.93s; gui_editor_window PASS8.29s.
  Export implementation is unchanged. All raw logs are under tools/.

Commands: cmake --preset dev -DPUTGD_AWS_RUNTIME_DIR=$PWD/build/sdk/lib;
cmake --build --preset dev --target test_capture_preparation test_editor_window test_editor;
ctest --preset dev -R '^capture_preparation_x11$';
ctest --preset dev -R '^(gui_editor_window|editor_contract)$'.
The focused GUI invocation selects redactionEdgesNeverSampleCoveredContent.
Bus socket preflight /tmp/putgd-a11y-XXXXXX/bus:26 UTF8 bytes, below107.

## Pictures

A pair: a-before-final.png and a-after-final.png show the real EditorWindow
on Aurora's native Plasma/Wayland desktop, Qt6.11.2-3.fc45. The exact f44-built
binaries above were copied unchanged; ldd found no missing libraries. Aurora
was used because f44 was leased by the recording lane. Both show Fit77%; the
left arrow calls out the thin tinted line present before and absent after.
The bottom-right arrow shows the other mask corner. Text/arrows were applied
using the production EditDocument/Commands renderer (tools/pg-pictures.cpp and
pg-annotate.cpp). Original single-arrow pictures are retained too.
The synthetic source has a magenta rectangle exactly covered by its redaction.
The images contain only the app's own surface, checked visually after capture.

Aurora was visibly unlocked and idle before launch on the wall tile5976.
Lease small-fixes-1377-1379 ran02:03:54–02:05:29UTC. Wayland socket24 bytes,
session bus18, private runtime session suffix30 bytes. The driver initially
called app.quit without handling the editor's discard flow; it stayed open.
Its two exact owned PIDs1146066 and1146626 were terminated after their pictures
were saved. No user's window was touched. Final console was visibly idle;
clean release receipt is2026-11-10T02-05-29Z-release.json on Aurora.

B pair: b-before.png and b-after.png are actual xterm captures on f44 in a
private Xvfb, displaying excerpts of the preserved f44 test results. They are
result illustrations, not physical-desktop support evidence. Annotation uses
the same production editor renderer. Xterm was installed with sudo-n dnf
install xterm; no general upgrade. tools/pg-term-capture.sh reproduces capture.

## Scope and retention

No uploads, credentials, existing user objects, bucket settings, desktop
restarts, VMs, audio or recordings were involved. No docs in the source repo
changed. No full release matrix, packages, memory/performance campaign or
other physical-desktop acceptance was run. Those are not claimed by these
focused fixes. SDK/source/build scratch is retained as a reusable isolated
builder cache; no scratch processes, displays, tunnels or leases are retained.
