# Acceptance checklist: scrolling capture on all five desktops (PR #1528)

For one acceptance worker per desktop: Plasma 6.8.2 (aurora-amd) or 6.6 (k72), Cinnamon X11 (m74), GNOME 50 (f44),
Hyprland (the Omarchy guest), Budgie (labwc, the Fedora 45 Budgie guest).

## Setup

- **Build.** The packages of PR #1528's CI run named in the PR description (the final head): the Fedora 44/45 RPM, the Debian or
  Ubuntu DEB, the Arch package, or the AppImage. Prove the identity with `putgd-cli diagnostics` (`build.gitTree` equals the
  tree in the PR description).
- **GNOME.** After installing, **log out and back in once** (`sudo -n systemctl restart gdm` on f44) so the Shell loads
  extension **24**; check `gnome-extensions info putgd@put.gd` (Version 24, ACTIVE). Save both lists first
  (`gsettings get org.gnome.shell enabled-extensions` and `disabled-extensions`) and restore them exactly at the end.
- **Lab rules.** One desktop lock at a time (`tools/lab/desktop_lock.py acquire HOST ...`, check it succeeded, heartbeat,
  release when not driving, none between 11:45 and 13:30 UTC). Every ssh, scp and rsync in the pinned form with
  `-o BatchMode=yes`. Local save only: no upload and no copied link (a lab resident with its own config whose every
  destination is `local`; see `r3-gnome/lab/resident.sh` and the "Lab resident" line of the GNOME recipe below). Windows
  opened by the run only; never `pkill -f`, never `rm -rf` a directory.
- **Helper log.** `PUTGD_RECORD_DEBUG_LOG=FILE` in the resident's environment; every row below reads it.
- **Input.** A relative mouse from `/dev/uinput` (`lab/umouse.py`: `m DX DY`, `w N` turns the wheel, `d`/`u` button),
  with flat acceleration (Plasma: KWin `pointerAccelerationProfileFlat`; GNOME: `gsettings set
  org.gnome.desktop.peripherals.mouse accel-profile flat`, restore `default`; X11: `xinput set-prop ... "libinput Accel
  Profile Enabled" 0 1 0`). On m74 `/dev/uinput` is root's: XTest from a separate client (`xdotool click 4/5`) is the wheel.
  Wall VNC is an absolute pointer and hides pointer bugs: never use it for the pause rows.
- **Pages.** Wikipedia "Linux", Stack Overflow 11227809, the GitHub pull request 1398, Python's `stdtypes` (dark theme in
  Chrome), the Al Jazeera article (`lab/sess.py` lists them), in Firefox, and in Chrome where it runs (Plasma, Cinnamon).
  `lab/sess.py BROWSER SITES MODES` drives one site per fresh browser; `LAB_NAV_JS=1` loads a page as if typed (Al
  Jazeera in Firefox).

## Rows

1. **You scroll** (default, `driver: user`), each page, each browser. Pass: no `scroll inject:` and no `scroll step:` line;
   `endReason: done`, `truncated: false`, `scrolledBy: user`; the image against the browser's own full-page picture
   (`lab/score.py`, tolerant bands) 95% or more of 64-row bands equal outside what the page pins; a sticky header once.
   Report `framesPlaced`/`framesSkipped` and the frame rate (`scroll: source N frames ... per second`, 20 or more).
   A page that lays itself out again after the capture passed (the article's video playlist strip, 220 px; GitHub's
   re-wrap in Chrome) differs from the browser's later picture by that much: find where with `r4/lab/where.py` and
   look with `r4/lab/seam.py` before calling rows lost (round 4 of the README).
2. **Auto-scroll** (`driver: putgd`), same pages. Pass: `end_of_content`, or `done` with `reachedEnd: true` and frames
   skipped, or `height_cap`; the whole page; seconds per 10,000 px (from `elapsedMs` and `height`). Chrome on the Python
   docs: no unwritten or undrawn cells (`lab/unwritten.py` reports 0). Hyprland: no painted arrow in the image. The
   GitHub pull request in Chrome is expected to be handed back near 36,300 px (the column re-wraps: row 7).
3. **The bar's states**, a picture of each on the real desktop: **Scroll the page** (waiting), **Following**, **Lost the
   page / Scroll back a little** (after row 7's jump), **Auto-scrolling**, **Paused: you moved the mouse**, **Auto-scroll
   lost the page**, **Found the page again**, **Saving…**. The words and the one fixed size as in the UI catalog
   (`scroll-bar-*`).
4. **Done by the key.** Bind a `scroll` hotkey; the bar names it ("Done or KEY when you reach the end"); pressing it
   during a capture keeps the image. Cinnamon: Esc finishes too, and still reaches the page. Without a binding the bar says
   "Done when you reach the end" (no key on Wayland).
5. **A region that fills the screen.** The bar sits inside the region's bottom-right corner (log: `scroll: no room beside
   the rectangle` or, on GNOME, `the Shell put the bar at ... inside`). Both drivers. Pass: no bar pixel anywhere in the image
   (`lab/barcheck.py RUN X0 X1` over the bar's columns finds only page content), the page whole, `hiddenCells` and
   `hiddenRows` in the result; Done and Cancel on the inside bar work.
6. **The pause by the mouse**, 10 tries from a fixed start (2 s) and 10 from a random one (1 to 6 s) with the relative mouse
   to Done at 600 px/s (`r3-gnome/lab/trial.py --rel --stop auto` on GNOME; give `--stop X,Y` from the log line `scroll: bar
   at ...; ... done X,Y WxH` elsewhere). Pass: the first click stops the capture in every try; no `scroll inject:` after the
   first motion except at most one `pointer put back`. **GNOME twice:** with extension 24 loaded (log: `the Shell watches the
   pointer`; expect 10/10 and 10/10), and with extension 23 still loaded after an update without a re-login (no Shell watch:
   the bar's window alone; report the numbers). Then once: a mouse move during auto-scroll, a little scrolling, **Auto-scroll**
   again: one exact image, `scrolledBy: both`.
7. **Lost and found.** You scroll: a jump of 25 notches at once (`LAB_JUMP=1`): the bar says **Lost the page**; scrolling back
   as it asks returns to **Following**, and the image is exact. Auto-scroll: the GitHub pull request in Chrome (or a press of
   End during auto-scroll elsewhere, from a separate uinput keyboard): **Auto-scroll lost the page**; scroll back: **Found the
   page again** (`activity: paused`, `pausedBy: lost`); the bar's **Auto-scroll** carries on (`LAB_RESUME=1` in `sess.py`
   takes the three pictures and presses the real button).
8. **Done takes the screen as it is.** In row 1's runs the helper log has `scroll fresh frame:` just before `scroll: ended
   Finished` and `scroll: Done's fresh frame added N rows` (also `stats.rowsAtDone` in the result); the image's last screen
   equals the browser's at that scroll position.
9. **Agent control.** The same capture through `putgd-cli` and through MCP: `scroll.prepare {rect, driver}` /
   `prepare_scroll_capture`, `scroll.autoScroll {on}` / `control_scroll_capture auto_scroll`, `scroll.inspect` /
   `get_scroll_capture` with `activity`, `driver`, `paused`, `pausedBy`, `placed`, `skipped`; `scroll.stop` keeps the image,
   `scroll.cancel` leaves no History row and no staging files. A toggle sent while the capture stops is refused with
   `scroll_state` and the capture goes on.
10. **A blank stretch taller than the region** (`lab/blank.html`): auto-scroll stops at it and ends `done` with
    `reachedEnd: false` and the note "auto-scroll stopped where the page showed nothing"; you scroll: lost after it (the
    documented limit).

## Cleanup (every desktop)

No putgd, putgd-record or lab browser process, no surface of put.gd on screen (a picture of the desktop), the lab mouse
gone, acceleration restored, on GNOME both extension lists as saved and the extension of the installed package (or none,
as before) after a last re-login, packages installed for the run removed (`dnf remove --noautoremove` / `apt remove`), the
lab directories kept, every lock released with `--verified-clean`.

## Recipes and tools in this record

- `lab/`: `sess.py` (real pages, both drivers; `LAB_TAG`, `LAB_RECT`, `LAB_URL`, `LAB_NAV_JS`, `LAB_RESUME`, `LAB_JUMP`,
  `LAB_BUILD`, `LAB_MAX`), `umouse.py`, `score.py`, `unwritten.py`, `barcheck.py`, `blank.html`.
- `r4/lab/`: `build-rel.sh` (an optimised lab build), `r4.sh` (round 4's runs), `where.py` (where an image row is in the
  browser's picture), `seam.py` (image beside picture at chosen rows), `tails.py` (images' last rows), `banner.py` (rows of
  a banner's colour above the last screen), `side.py`, `slice.py`.
- `r3-gnome/lab/`: `trial.py` (the pause tries), `tries.sh`, `resident.sh` (a lab resident with its own config),
  `relogin.sh` (an extension version, a re-login, out of the overview), `envgen.sh` (the session's environment over SSH).
