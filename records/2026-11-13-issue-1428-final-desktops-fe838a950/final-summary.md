Final desktop acceptance report for #1428 — **not accepted against the complete plan**.

Eight Wayland desktop/package cells have observed successful primary text pipelines. The visible selector does not meet decision 14's “Copies text” requirement; Quick redact also masked an extra word in this synthetic fixture. GNOME/X11 and KDE/X11 remain **not run** for the distinct reasons below. This report does not establish the measurement worker's quality, latency or memory gates, and is not a merge recommendation.

Candidate **fe838a9502167672f3512e27c32c74cfcf6c84d1**, version **26.1113.4836-dev+gfe838a950216**. All packages came from the shared [CI run 43394391197](https://github.com/patrick-hudson/put.gd-desktop/actions/runs/43394391197), now completed successfully; [completion receipt](https://github.com/patrick-hudson/put.gd-evidence/tree/618cfe4c8d4b2d854a9c51c50a16bb3daa843bc4/records/2026-11-13-issue-1428-final-desktops-fe838a950/ci-completion.json). No put.gd compilation on a desktop or guest, no product changes, no product pushes or pull request.

Package identities (the package ID in each row resolves to this full filename/hash):

| ID | Package | SHA-256 |
|---|---|---|
| R | `putgd-26.1113.4836~dev+gfe838a950216-1.fc44.x86_64.rpm` | `e33add66f261ff3dac5b39e01c37058dad7983e8a6c53ccbd09226b7e3eba0ff` |
| D | `putgd_26.1113.4836~dev+gfe838a950216_amd64.deb` | `72fd93c6b23541e1a40c90f963925f033e2b286ecfd63dc392c462a69acf4829` |
| A | `putgd-26.1113.4836-dev+gfe838a950216-x86_64.AppImage` | `0d3f1ae79e7691c40d3ac884d8290b150763599b2a484a7fd614d8878cf33188` |

Native dependencies were resolved through the distro package manager. AppImage feature cells used the actual FUSE-mounted AppImage; the matching extracted image supplied its CLI client. Only the guest missing-helper/data tests altered an extracted copy. Aurora used the permitted AppImage fallback: no overnight Atomic layering/reboot of its staged OS deployment.

Every primary PASS below means the independent clipboard client first verified its sentinel, the actual region was selected over my synthetic text window, and independent `wl-paste` then returned exactly these 58 characters (no trailing newline):

```text
ALPHA BRAVO CHARLIE
SYNTHETIC TEXT 1428
hello@example.test
```

Hotkey means a real assigned keyboard chord (removed afterward). Window means an actual pointer click on the command band. Tray means the tray's public **dbusmenu Event(41, "clicked")** entry activation, the approach used in #1442, rather than a pointer click on the panel. Editor and History operations below were driven through production CLI/session methods with their rendered windows reviewed; this is not a claim of pointer-driving every editor/History control. The retained [drivers](https://github.com/patrick-hudson/put.gd-evidence/tree/618cfe4c8d4b2d854a9c51c50a16bb3daa843bc4/records/2026-11-13-issue-1428-final-desktops-fe838a950/drivers) show the exact method.

The numbers are each operation's `text.inspect.totalMs`, not a performance acceptance result. “exit 0” comes from the kernel process watcher; “gone” means an empty helper-process check after the operation, without a collected numeric exit status.

| Cell / package | Hotkey → exact paste | Tray → exact paste | Window → exact paste | Helper after each | Receipts |
|---|---|---|---|---|---|
| f44 Fedora 44 GNOME Wayland / R | PASS 225 ms | PASS 237 ms | PASS 297 ms | exit 0 | [primary](https://github.com/patrick-hudson/put.gd-evidence/tree/618cfe4c8d4b2d854a9c51c50a16bb3daa843bc4/records/2026-11-13-issue-1428-final-desktops-fe838a950/f44-attempt2) |
| k72 Kubuntu 26.04 Plasma Wayland / D | PASS 290 ms | PASS 302 ms | PASS 298 ms | exit 0 | [primary](https://github.com/patrick-hudson/put.gd-evidence/tree/618cfe4c8d4b2d854a9c51c50a16bb3daa843bc4/records/2026-11-13-issue-1428-final-desktops-fe838a950/k72-native) |
| k72 Plasma Wayland / A | PASS 181 ms | PASS 142 ms | PASS 140 ms | exit 0 | [raw observations](https://github.com/patrick-hudson/put.gd-evidence/tree/618cfe4c8d4b2d854a9c51c50a16bb3daa843bc4/records/2026-11-13-issue-1428-final-desktops-fe838a950/k72-appimage) + [visual retake](https://github.com/patrick-hudson/put.gd-evidence/tree/618cfe4c8d4b2d854a9c51c50a16bb3daa843bc4/records/2026-11-13-issue-1428-final-desktops-fe838a950/k72-visual-retake) |
| aurora-amd Fedora 45 Atomic Plasma Wayland / A | PASS 98 ms | PASS 66 ms | PASS 83 ms | exit 0 | [initial](https://github.com/patrick-hudson/put.gd-evidence/tree/618cfe4c8d4b2d854a9c51c50a16bb3daa843bc4/records/2026-11-13-issue-1428-final-desktops-fe838a950/aurora-initial) + [corrected pointer](https://github.com/patrick-hudson/put.gd-evidence/tree/618cfe4c8d4b2d854a9c51c50a16bb3daa843bc4/records/2026-11-13-issue-1428-final-desktops-fe838a950/aurora-pointer) |
| Fresh Ubuntu 26.04 GNOME Wayland guest / D | PASS 368 ms | PASS 259 ms | PASS 255 ms | gone | [receipt](https://github.com/patrick-hudson/put.gd-evidence/tree/618cfe4c8d4b2d854a9c51c50a16bb3daa843bc4/records/2026-11-13-issue-1428-final-desktops-fe838a950/ubuntu-native) |
| Same fresh Ubuntu guest / A | PASS 193 ms | PASS 144 ms | PASS 128 ms | gone | [receipt](https://github.com/patrick-hudson/put.gd-evidence/tree/618cfe4c8d4b2d854a9c51c50a16bb3daa843bc4/records/2026-11-13-issue-1428-final-desktops-fe838a950/ubuntu-appimage) |
| Fresh Budgie/labwc guest / A | PASS 166 ms | PASS 123 ms | PASS 122 ms | gone | [receipt](https://github.com/patrick-hudson/put.gd-evidence/tree/618cfe4c8d4b2d854a9c51c50a16bb3daa843bc4/records/2026-11-13-issue-1428-final-desktops-fe838a950/budgie) |
| Fresh Omarchy/Hyprland 0.56.2-4 guest / A | PASS 412 ms | PASS 123 ms | PASS 154 ms | gone | [receipt](https://github.com/patrick-hudson/put.gd-evidence/tree/618cfe4c8d4b2d854a9c51c50a16bb3daa843bc4/records/2026-11-13-issue-1428-final-desktops-fe838a950/hyprland) |
| GNOME/X11 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | No matching launch profile; see below |
| KDE/X11 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | Patrick's apps present; see below |

Other per-cell checks:

| Cell / package | Region QR → content | Editor selected words → paste | Quick redact email | History Copy text | Show QR visible + saved PNG independently decoded | Visible selector |
|---|---|---|---|---|---|---|
| f44 / R | PASS 172 ms | PASS | FAIL* | PASS | PASS | FAIL: generic hint |
| k72 / D | PASS 214 ms, corrected fixture | PASS | FAIL* | PASS | PASS | FAIL: generic hint |
| k72 / A | PASS 104 ms | PASS, retake verified | FAIL* | PASS | PASS, retake verified | FAIL: generic hint |
| Aurora / A | PASS 49 ms, corrected foreground | PASS | FAIL* | PASS | PASS | FAIL: generic hint |
| Ubuntu / D | PASS 217 ms | PASS | FAIL* | PASS | PASS | FAIL: no hint in retained frame |
| Ubuntu / A | PASS 100 ms | PASS | FAIL* | PASS | PASS | FAIL: no hint in retained frame |
| Budgie/labwc / A | PASS 98 ms | PASS | FAIL* | PASS | PASS | FAIL: generic hint |
| Omarchy/Hyprland / A | PASS 125 ms | PASS | FAIL* | PASS | PASS | FAIL: generic hint |

Region QR expected/pasted `https://example.test/acceptance/1428`. Editor selected/copy pasted exactly `ALPHA BRAVO CHARLIE`. History retained an owned synthetic image through the production upload pipeline to a credential-free loopback HTTP receiver; no user objects or credentials were used. History copied the same three-line text. The Show QR windows were seen with a code; all nine saved PNG independent decode files, including the k72 retake, equal `https://example.test/acceptance/1428/image.png`. f44 additional receipts: [History](https://github.com/patrick-hudson/put.gd-evidence/tree/618cfe4c8d4b2d854a9c51c50a16bb3daa843bc4/records/2026-11-13-issue-1428-final-desktops-fe838a950/f44-supplement) and [Show QR](https://github.com/patrick-hudson/put.gd-evidence/tree/618cfe4c8d4b2d854a9c51c50a16bb3daa843bc4/records/2026-11-13-issue-1428-final-desktops-fe838a950/f44-history-qr); k72 corrected QR: [receipt](https://github.com/patrick-hudson/put.gd-evidence/tree/618cfe4c8d4b2d854a9c51c50a16bb3daa843bc4/records/2026-11-13-issue-1428-final-desktops-fe838a950/k72-native-qr-corrected).

*Quick redact's email category was exercised successfully as an action (`email: 1`), but generated two ordinary redaction rectangles: one over the email and another over the preceding `1428`. I am flagging this observed overreach as a miss, not claiming accurate category-only redaction or performing the other worker's corpus scoring. Screenshots and rectangle coordinates are retained in each editor receipt. The same extra mask is visible in the k72 retake.

The generic visible selector hint is **“Drag to select · Esc to cancel”**, with no “Copies text”. That was actually seen on f44, k72 native/AppImage, Aurora, Budgie and Hyprland. Ubuntu native/AppImage retained pre-drag screenshots have **no visible hint**; the earlier comment that copied f44's wording to Ubuntu was explicitly corrected. I did not measure accessible descriptions, and do not substitute one for the missing visible outcome hint.

Additional required checks:

| Check | Result | Reason / evidence |
|---|---|---|
| Six direct `text.recognize` sources per tested desktop: region, window, monitor, desktop, clipboard, file; plus History through `history.copyText` | PASS for text or the adapter's own capability refusal | All returned text except Budgie/labwc window, which advertised unavailable and returned `window_unavailable` because the compositor lacks its required capture protocol. Aurora window was re-run with the external fixture foreground and returned text. Source records are in each cell's receipt; this is six direct sources plus the History action, not seven direct-source calls. |
| Missing helper, guest only | PASS | `text_helper_missing`, reinstall guidance, sentinel unchanged; helper restored. [receipt](https://github.com/patrick-hudson/put.gd-evidence/tree/618cfe4c8d4b2d854a9c51c50a16bb3daa843bc4/records/2026-11-13-issue-1428-final-desktops-fe838a950/unavailable/helper-and-data.json) |
| Missing English data, guest only | PASS | `engine_unavailable`, English-package guidance, sentinel unchanged; bundled file hash restored and distro English package reinstalled. Same receipt. |
| Actually locked screen | PASS | Budgie Super+L; monitor request ended `session_locked` with unlock guidance/no result. Visibly unlocked afterward; sentinel unchanged and helper absent. [receipt](https://github.com/patrick-hudson/put.gd-evidence/tree/618cfe4c8d4b2d854a9c51c50a16bb3daa843bc4/records/2026-11-13-issue-1428-final-desktops-fe838a950/budgie/receipt.json) and lock/unlocked frames. |
| History item without retained local image | PASS | Owned synthetic local file temporarily moved: `artifact_missing`, “Cannot read the retained local copy”, clipboard unchanged; file restored. [receipt](https://github.com/patrick-hudson/put.gd-evidence/tree/618cfe4c8d4b2d854a9c51c50a16bb3daa843bc4/records/2026-11-13-issue-1428-final-desktops-fe838a950/f44-supplement/receipt.json) |
| Command band at real minimum width, normal text | PASS | f44 1060 px enforced minimum, actual resize gesture, visually reviewed. [receipt/frame](https://github.com/patrick-hudson/put.gd-evidence/tree/618cfe4c8d4b2d854a9c51c50a16bb3daa843bc4/records/2026-11-13-issue-1428-final-desktops-fe838a950/f44-normal-text) |
| Command band at real minimum width, 150% app text | PASS | f44 same minimum; icon controls fit. [receipt/frame](https://github.com/patrick-hudson/put.gd-evidence/tree/618cfe4c8d4b2d854a9c51c50a16bb3daa843bc4/records/2026-11-13-issue-1428-final-desktops-fe838a950/f44-large-text) |
| GNOME extension 23 active | PASS on f44 and Ubuntu native/AppImage | f44 system extension23 after checked logout/login; Ubuntu system23 for DEB, then managed user23 ACTIVE for AppImage after login step. No Patrick applications were logged out. |
| Old loaded extension22 refusal + other recording hotkey | NOT RUN | f44 began without put.gd and with its extension disabled; Ubuntu golden had loaded v1, not v22. No v22 state was claimed or fabricated. |
| GNOME/X11 pipeline | NOT RUN | Candidate `tools/lab/profiles/*.yaml` has no GNOME/X11 launch profile. A surface-driver JSON and stored Ubuntu24 X11 golden are not that launch profile; no Cinnamon relabeling. [inventory](https://github.com/patrick-hudson/put.gd-evidence/tree/618cfe4c8d4b2d854a9c51c50a16bb3daa843bc4/records/2026-11-13-issue-1428-final-desktops-fe838a950/x11-rows/profile-and-permission.json) |
| KDE/X11 pipeline | NOT RUN / BLOCKED | k72 supplies `plasmax11.desktop`, but pre-logout check found Patrick's Konsole PID2014802 and btop PID2014817. Owner away is not permission to log those out. No logout or display-manager change. [preflight](https://github.com/patrick-hudson/put.gd-evidence/tree/618cfe4c8d4b2d854a9c51c50a16bb3daa843bc4/records/2026-11-13-issue-1428-final-desktops-fe838a950/k72-appimage/k72-x11-preflight.txt) |
| Aurora native layered RPM | NOT RUN | Authorized AppImage fallback used to preserve Atomic staged deployment. |

Initial harness failures are preserved rather than turned into passes: f44 wrong screen geometry/clipboard timeout; first guest SSH port pin mismatch and a later corrupt copied driver after an unclean reset; k72 missing QR fixture; Aurora foreground/geometry setup; and k72 AppImage cleanup's cross-filesystem rename failure. The latter happened after feature observations but before its final receipt: `observations.json` explicitly reconstructs the unchanged raw JSON lines, not a fabricated original receipt. Corrections have separate receipts. The initial k72 AppImage editor/QR frames were blank; that claim was withdrawn, a new lease taken, and the retake frames actually reviewed. The original f44 minimum-width attempt expanded/moved the window and is not the sizing pass. Every isolated app used short private runtime paths; byte-length preflight and ownership checks remained intact.

No quality score, p95 latency, 180-second memory/residency gate, or helper-failure campaign is claimed here. The reused watcher incidentally records RSS, but that is not memory acceptance. m74 and d69 were not used for SSH, testing or VM hosting. Their measurement worker owns those gates.

Lab state left:

- All own physical leases released after cleanup checks: f44 **09:00:43 UTC**, Aurora **09:25:50 UTC**, k72 final retake **09:40:07 UTC**, before 12:15 UTC. [final lock status](https://github.com/patrick-hudson/put.gd-evidence/tree/618cfe4c8d4b2d854a9c51c50a16bb3daa843bc4/records/2026-11-13-issue-1428-final-desktops-fe838a950/lab-final-state/final-lock-status.txt); Aurora's exact release receipt is under [restoration](https://github.com/patrick-hudson/put.gd-evidence/tree/618cfe4c8d4b2d854a9c51c50a16bb3daa843bc4/records/2026-11-13-issue-1428-final-desktops-fe838a950/aurora-restoration).
- f44 had no put.gd package initially and has none now. Its original enabled/disabled GNOME extension sets, including the deliberately disabled put.gd extension and AppIndicator state, were restored. **Unresolved restoration side effect:** the scoped DNF install invalidated a pre-existing offline transaction. The warning is retained; I did not queue a replacement or run a broad upgrade. [receipts](https://github.com/patrick-hudson/put.gd-evidence/tree/618cfe4c8d4b2d854a9c51c50a16bb3daa843bc4/records/2026-11-13-issue-1428-final-desktops-fe838a950/f44-restoration).
- k72 had no installed put.gd (`rc 26.1112.4660~nightly`); candidate removed, now `rc 26.1113.4836~dev+gfe838a950216`. Thus the installed-package state is restored but dpkg's residual-config version metadata changed. Existing configuration retained. Temporary hotkeys/input/app removed, newly created AppImage data retained privately outside its default location. Patrick's apps and pre-existing headless residents preserved; no logout. [restoration](https://github.com/patrick-hudson/put.gd-evidence/tree/618cfe4c8d4b2d854a9c51c50a16bb3daa843bc4/records/2026-11-13-issue-1428-final-desktops-fe838a950/k72-restoration) and [final retake cleanup](https://github.com/patrick-hudson/put.gd-evidence/tree/618cfe4c8d4b2d854a9c51c50a16bb3daa843bc4/records/2026-11-13-issue-1428-final-desktops-fe838a950/k72-visual-retake).
- Aurora had/has no native put.gd; staged OS deployment and pre-existing process4102 preserved. Temporary app/hotkey/input removed; newly created data retained privately. AppImage fallback only.
- All three fresh guests were hosted on f44, displayed on the live wall, and retired by guarded lab cleanup only after exported evidence/checksum verification: Ubuntu `g2`, Budgie `b1`, Hyprland `h1`. Their immutable golden sources were preserved; all owned overlay paths are now absent. [retirement verification](https://github.com/patrick-hudson/put.gd-evidence/tree/618cfe4c8d4b2d854a9c51c50a16bb3daa843bc4/records/2026-11-13-issue-1428-final-desktops-fe838a950/lab-final-state/remote-resources.json) plus each guest's cleanup receipt. Cleanup outcomes honestly record the selector miss as failed acceptance.
- Guest wall tiles/tunnels removed; original five physical wall entries preserved. The temporary decoder container and its newly pulled Ubuntu image were removed. No remaining owned guest or desktop input agent. Private host-side evidence/run identities retained. Workstation source is clean at exact candidate SHA.

All links above pin the evidence commit. The desktop functional pipelines worked, but the visible selector miss, Quick redact overreach and explicitly unrun X11 coverage remain for the coordinator. **No full desktop acceptance is claimed.**
