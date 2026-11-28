# f44 scrolling-capture harness: GitHub and Python docs rows run again (#2077)

The f44 (GNOME) port of the scrolling-capture lab harness failed before any capture on its GitHub and Python docs rows (#2077), on every build. This record holds the fixed harness and a run of every row on f44 with it. The harness is `sess.py` and `live7.py` from `records/2026-11-25-autoscroll-pacing-2000/harness/`. That record is left as it was run. `harness/changes.diff` is the whole change against it.

## What was wrong, and the fix

1. **Python docs, stale URL.** Python 3.15's documentation moved `library/stdtypes.html` to `builtins/stdtypes.html`, so the page check saw a different path. `PAGES['python']` is now the new URL. The article check was Wikipedia's `#mw-content-text` for every page but GitHub, so it would have failed next. Each page now has its own (`ARTICLE`, `div.body[role="main"]` for the Python docs).
2. **GitHub, error page.** The pinned `vinta/awesome-python` blob served GitHub's "Unicorn!" page to the lab browser. The row now uses PR #1398, as the m74 and aurora harnesses do.
3. **Marionette, second connection refused.** Firefox keeps one Marionette session, and `browser_start()` left its own session open when `run()` connected again ("an active session has been found"). The changes:
   - `Marionette.close()` ends the session and the connection.
   - `browser_start()` and every run close theirs.
   - `connect()` retries for up to 10 s while Firefox lets go of the old session.
   - `DevTools` got a `close()` too.
4. **Found during this run: VNC port.** `sess.py` hardcoded VNC port 5900 for the user rows' pointer move and its screenshots, while f44's wall VNC is 5901 (`SF7_VNC`, which `live7.screen_png` already read). Every user row failed with `ConnectionRefusedError` once the pages loaded. The older f44 runs here were auto-only, so they never reached that code. `sess.py` now takes the port from `SF7_VNC`.

## Setup

- f44: Fedora 44, GNOME Shell Wayland, physical session shown on the display wall. The putgd@put.gd and AppIndicator extensions were enabled, and the desktop lock (`desktop_lock.py run f44`) confirmed the tray host was serving.
- Lock: one lease from 2026-11-28T02:03:46Z to 02:23:49Z (owner `opus-2077`).
- put.gd: the published nightly 26.1126.7275, `putgd-26.1126.7275-nightly-fedora44-x86_64.rpm` from the release, installed with `sudo dnf install ./…rpm` over 26.1125.7045, as a user would. The upgrade was directed by the Sr Manager. The lock's release lists the package under `--not-mine`, since its tool has no field for an upgrade kept on purpose. The dnf transaction upgraded only `putgd`. It invalidated a pending GNOME Software (dnf5daemon) offline transaction, which was left that way: lab hosts take no broad upgrades.
- Lab driver `test_scroll_capture_driver`: built on f44 from a blobless clone at `v26.1126.7275-nightly`, with `PUTGD_RELEASE_TAG` set (`harness/drv.sh`; the build was finished at `-j2` beside another session's build). Its `build-info.json` (`logs/driver-build-info.json`: commit 2763822436b8, count 7275, clean, provenance git) is byte-identical to the package's `/usr/share/putgd/build-info.json` (`series.sh` checks with `cmp`).
- Firefox 158.0.1, a fresh profile per page. Wheel from `harness/umouse.py` (relative uinput mouse). Series: `harness/series.sh`.

## Results (`runs/`, third pass)

| Page | You scroll | Auto-scroll |
| --- | --- | --- |
| GitHub PR #1398 | `done`, 40,190 rows = page, 0 skipped | `done`, 40,190 rows = page, 33 skipped |
| Python docs, `builtins/stdtypes.html` | `height_cap` at the harness's 60,000-row limit (`LAB_MAX`; the page is 110,214), 0 skipped | `height_cap` at 60,000, 0 skipped |
| Wikipedia, Linux (control) | `done`, 24,094 rows = page, 0 skipped | `end_of_content`, 24,094 rows = page, 0 skipped |

Every row loaded its page and passed the page and article checks, and its capture ran. No Marionette connection was refused, across four fresh browsers in three passes. GitHub's auto-scroll ended `done` rather than `end_of_content` because frames were skipped. That is the app's rule (an end of content promises no skipped frame), and #2064's m74 recheck saw the same on GitHub. It is not a harness failure.

Earlier passes (`logs/`):
- Pass 1 refused every capture through the harness's own load guard (1-minute load 5.6 to 6.4: another session's build, and Firefox starting). The pages and Marionette were already fine in that pass.
- Pass 2 found the VNC port bug.
- Pass 3, after both, is the one above.
