# PR 1532 tray and action bar acceptance — incomplete

This is a partial real-desktop campaign, not five-desktop acceptance. Many requested sequences were not completed. NOT RUN includes partially exercised rows; it never implies a pass. No product source was changed, no build was compiled, and no PR comment, issue or merge was made.

The checkout was fetched and detached at f63d24dbcef39f8744330bec7a80f2bc340092d5. CI run 43643204150 supplied the native DEBs/RPM and AppImage. CI compiled merge commit b91a65c2ee63aac84093343a384ff085ad0c0f42; its tree is exactly the requested head's tree, **7290d67885b6782efd871ac7b1c2d1787e03e525**. Every tested candidate resident's diagnostics reported that tree. See the five `*-identity.json` files. Frames here are real full RFB frames, unmasked and uncropped; catalog images are not used as desktop proof.

| Row | KDE | GNOME | Cinnamon | Budgie | Hyprland |
|---|---|---|---|---|---|
| T1 | PASS | PASS | PASS | PASS | PASS |
| T2 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| T3 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| T4 | PASS | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| T5 | PASS | FAIL | FAIL | FAIL | FAIL |
| T6 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| T7 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| T8 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| T9 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| T10 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| T11 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| T12 | FACT | NOT RUN | NOT RUN | FACT | FACT |
| T13 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| W1 | PASS | PASS | PASS | NOT RUN | NOT RUN |
| W2 | PASS | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| W3 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| W4 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| W5 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| W6 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| W7 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| W8 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| W9 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| W10 | PASS | PASS | NOT RUN | NOT RUN | NOT RUN |

T12 uses FACT where an observation was obtained, because the checklist explicitly gives it no pass/fail verdict.

## Checked rows and evidence

- T1: [KDE](k72-tray.png), [GNOME](f44-tray.png), [Cinnamon](m74-tray.png), [Budgie](budgie-tray3.png), [Hyprland top](omarchy-menu-no-tooltip.png) and [Hyprland bottom](omarchy-menu-scrolled.png). Hyprland's root menu scrolls; both portions were inspected. All show the requested groups and retired app rows are absent.
- T4 KDE: [output submenu](k72-output.png), then [Change output opens Settings → Capture](k72-change-output.png). This profile uses all-local outputs; there are no output exceptions to display.
- T5 KDE: [native tray](k72-tray.png) shows hints only for the configured bound region/window/desktop actions. Its host formats shifted digit keys as Ctrl+!, Ctrl+@ and Ctrl+#.
- W1: [KDE](k72-window2.png), [GNOME](f44-history2.png), [Cinnamon](m74-window.png): fresh private window state, 1440×880, nine buttons in one row with the divider and trailing pair. The 1280×800 Budgie guest clamps to the screen and wraps to two rows ([frame](budgie-start.png)); Omarchy tiles the window to 1260 pixels and wraps ([frame](omarchy-window.png)). Guest W1 remains NOT RUN because a 1440-pixel screen case was not exercised there.
- W2 KDE: [1060-pixel window](k72-narrow.png); a further resize attempt leaves the same minimum width ([frame](k72-minimum.png)). Full labels and the trailing pair remain visible.
- W10: [KDE](k72-hamburger.png), [GNOME](f44-hamburger.png): all four hamburger entries and ten Hotkeys rows with group gaps.

## Failures: missing shortcut hints (T5)

The bound Capture region, Capture window and Capture desktop hotkeys have no visible hints in these native menus. The identity receipts include the accepted binding state. Exact steps: start the candidate in the private profile; inspect diagnostics to confirm Ctrl+Shift+1 is bound; open the native menu with a real right click; inspect the action rows. KDE displayed the hints; other hosts did not.

- GNOME: [candidate](f44-tray.png), [published nightly](f44-nightly-menu.png). Native Shell 50.6, put.gd extension 23 ACTIVE and ready, AppIndicator ACTIVE. The menu was opened from the top panel while in Overview so the fullscreen cover did not hide the panel. The published nightly also omits the hints: **predates this PR**.
- Cinnamon: [candidate](m74-tray.png), [published nightly](m74-nightly-tray.png). Right-click the put.gd panel icon. The published nightly also omits the hints: **predates this PR**.
- Budgie and Hyprland: candidate [Budgie](budgie-tray3.png), [Hyprland](omarchy-menu-no-tooltip.png). The private golden's region hotkey was bound even with no output configured. The fresh Budgie nightly comparison also omits the hints ([frame](budgie-nightly-menu.png), [identity](budgie-nightly-identity.json)): **predates this PR**. The fresh Hyprland nightly comparison also omits them ([frame](omarchy-nightly-menu.png), [identity](omarchy-nightly-identity.json)): **predates this PR**.

The nightly comparator is published v26.1114.5000-nightly, commit df229be2990554bb9c4dff5a020e1407e4eb1885, tree 72e44106c147d2c855ff55044f59c85ce0b1b113. GNOME uses the published AppImage; Cinnamon uses the published Ubuntu 24.04 DEB extracted to a private prefix. Neither comparison writes the desktop keyring.

## T12 facts and other observations

- KDE: plain left click opened History from Settings ([frame](k72-left.png)). Middle and double clicks caused no visible change with History already visible; this does not establish that no activation signal was sent.
- Budgie: plain left click opened History ([frame](budgie-left.png)). Middle/double clicks left History visible.
- Hyprland/quickshell: plain left click opened the menu ([frame](omarchy-left.png)); double click also left the menu open. Middle click left the History window visible without the menu. History was already visible, so no view-switch conclusion is possible.
- GNOME and Cinnamon: the saved click attempts were confounded by Overview/cover/menu focus. No reliable plain/middle/double conclusion is claimed; T12 is NOT RUN for both.
- Quickshell constrains the root menu to a scrolling viewport and elides even this ordinary output label (`Capture output: Nothing…`). Its tooltip can cover the first row while the pointer stays on the icon. Moving the pointer into the menu removes it. These are host observations, not established PR regressions.
- KDE and GNOME render disabled submenu detail text in pale gray; it remains readable in these frames. No 50-character destination was tested.

## NOT RUN details

This campaign did not complete the full requested checklist. There is no broad acceptance claim.

- T2: both edit source actions were not completed. The driver attempts on Cinnamon blocked before usable tray targeting; manual screenshots do not prove editor/file chooser routing.
- T3: KDE's None/5-second radio states, note and relabel were observed, but the complete hotkey-delay toggle sequence was not retained unambiguously. Other hosts were not exercised through the full sequence.
- T4 on other desktops: no complete submenu-to-Settings sequence.
- T6–T9: upload/live recording/failure/update fixtures and simultaneous-state sequence were not run. No real upload destination or credential was used.
- T10: no long destination fixture was configured.
- T11: no complete window-edited delay/output/hotkey refresh sequence on each host. Some CLI setting changes were made on KDE; they do not establish this row.
- T13: no complete set of real capture actions, including scrolling to end_of_content, was run. Window navigation alone is insufficient.
- W2 outside KDE: no complete minimum-width enforcement sequence. A Cinnamon resize attempt was inconclusive.
- W3: enlarged desktop text was not tested.
- W4: isolated dropdown attempts were made, but not both split-button paths plus the negative right-click cases.
- W5: full keyboard opening, focus, Enter and Esc sequences were not run.
- W6: drag/drop and unavailable-region case were not run.
- W7: delay controls were seen on several pages, but all pages and text-elision priorities were not exercised.
- W8: no tooltip/timing/hotkey comparison sequence.
- W9: no recording phase/accessibility-description sequence.
- W10 outside KDE/GNOME: not fully exercised.

## Execution limits and preserved attempts

KDE's surface-driver preflight blocked on missing python3-pyatspi. No non-putgd package was installed to address it, per the brief. Cinnamon's first two tray recipes blocked on the tray icon accessibility selector. Its fullscreen cover initially hid the panel; changing that owned cover to maximized exposed the panel, but the driver still did not locate the icon. The bounded run was stopped with SIGTERM to its exact owned PID and completed cleanup. Its interrupted recipe is a driver failure, not a product failure. Manual VNC checks supplied the accepted frames. These setup receipts are retained separately.

The first 90-minute lock request was refused (maximum 45); the corrected request succeeded before host work. Short private socket paths were checked: native session sockets 39–40 UTF-8 bytes, native input socket path 24 bytes, guest QMP/VNC paths 55 bytes and guest session socket 46 bytes (limit 107). No harness/socket checks were weakened. Failed attempts remain in the private work directory.

## Hosts and restoration

All three physical hosts started with **no put.gd resident and no installed putgd binary**. This differs from the brief's assumption of a running published nightly. Their initial package states were: k72 `rc 26.1113.4926~dev+gff636bba2bee`, m74 `rc 26.1113.4757~nightly`, f44 RPM absent. The candidate was removed after testing; no pre-existing runtime could be restarted or have its version confirmed. The final dpkg `rc` residual version is the candidate version, so the package database is not byte-for-byte identical to the starting state. See `*-restored.txt`.

| Desktop | Execution host / system | Version basis | Final state |
|---|---|---|---|
| KDE | k72, Ubuntu 26.04.1, native Wayland | plasma-workspace 6.6.6 observed | candidate removed; no resident; lock cleanly released |
| GNOME | f44, Fedora 44, native Wayland | gnome-shell 50.6 observed; extension 23 ACTIVE during testing | candidate removed; second GDM re-login unloads extension; AppIndicator disabled again; original enabled-extension list preserved; no resident; lock released |
| Cinnamon | m74, Mint 22.3, native X11 | Cinnamon 6.6.9 observed | candidate removed; comparison resident stopped; cover stopped; lock released |
| Budgie | f44-hosted disposable fedora45-budgie VM | Fedora 45, Budgie 10.10.3, labwc 0.20.2; queried live in the fresh nightly comparator from the identical immutable golden (b2-export.txt) | candidate overlay b1 stopped and guarded cleanup completed |
| Hyprland | f44-hosted disposable Omarchy VM | Omarchy 4.5.0 and Hyprland 0.56.2 observed; see omarchy-version.txt | candidate overlay o1 stopped and guarded cleanup completed |

GNOME was initially deferred and retried after the candidate guests, so this run did not retain the brief's exact requested desktop order. Installing only putgd through DNF invalidated f44's pre-existing staged offline transaction; the install log explicitly reports it. No desktop package was installed/upgraded/downgraded and no general update command was run. That pending-transaction state was not restored. Physical put.gd runtime absence and AppIndicator enabled state were restored; the stronger claim that every host is exactly as it was would be inaccurate.

Candidate guest evidence archives were exported privately and SHA-256 matched before guarded retirement: b1 `862a140f90fe350cad6967d38e4874612e004d1a202ca07221947d5ad11f09ef`, o1 `dfa4b85f6e147ede241fd094f9c91d005cc949bc0184126f5ad46754e3a511ef`. Private archives can contain run SSH identities and are not published here. Only frames, selected receipts and identities are published. Goldens were not modified. All wall entries/tunnels created for completed guests were removed, preserving other entries.

Nightly comparator overlays b2 and o2 were also stopped, exported with matching checksums and retired through guarded cleanup. Their private bundle hashes are `7e3e2c52f1bb17f13e5e2084ff4eb7c4656c5d5fa4b30ff243c831c2279a3822` and `dba66500e95a9a6ad0ad335661f473b7cc9bb9fcb647926480005472331b7f19`. All four retirement receipts are included.
