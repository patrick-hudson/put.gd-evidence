# W7 KDE fix recheck — PASS

Requested head **f5b3d0a8744bfa4419e7c73cfeef045cc18e3284**, CI run **43655000640**, native Ubuntu 26.04 DEB. Running diagnostics reported tree **0807ddfa1d251264601ef76dc6f105452a317952**, equal to `git rev-parse f5b3d0a8744bfa4419e7c73cfeef045cc18e3284^{tree}`. CI's merge commit is eb3da9962dc898034ebc7d75304c1289c0066b73; running version **26.1114.5030-dev+geb3da9962dc8**. [Diagnostics](diagnostics.json).

Tested on k72, Ubuntu 26.04.1 / Plasma 6.6.6 / native Wayland, normal font. A new private profile used the same 50-character destination **Tray acceptance HTTP destination with a long label**, inherited for all capture actions, local copy kept, delay 5 seconds. [Accepted settings](settings.json). No credentials or upload receiver were needed. Private session socket was 36 UTF-8 bytes (limit 107).

Settings → General, 880-pixel height throughout:

| Case / full desktop frame | Output summary | Delay control | Settings save automatically | Version |
|---|---|---|---|---|
| [Initial 1440](W7-1440-initial.png) | Visible, full | Visible, whole | Visible | Visible |
| [Resize to 1200](W7-1200.png) | Visible, full | Visible, whole | Hidden | Visible |
| [Resize to 1060](W7-1060.png) | Visible, full | Visible, whole | Hidden | Hidden |
| [Back to 1440](W7-1440-final.png) | Visible, full | Visible, whole | Visible | Visible |
| [Fresh 1060](W7-1060-fresh.png) | Visible, full | Visible, whole | Hidden | Hidden |

The fresh case closed the 1060 window, verified its putgd-ui process had ended, then used production ui.show to create a new UI process (PID 1949653) at the retained 1060 × 880 size. It matches the resized case; the window is recentered. [KWin geometry witness](fresh-window-witness.json).

**W7 PASS:** summary always present, delay whole, and automatic-save text never appears without version text. The requested one-open [idle tray sanity frame](T1-idle-sanity.png) retains T1's order/grouping; the delay/output labels reflect this configured profile.

## Correction to previous W7 finding

The earlier report misread `r2/k72/W7-width1060.png`. Its output summary is visible in full. The fault was **Settings save automatically appearing while the build version was absent**. The new fix resolves that priority error. The previous summary-loss and summary-retention nightly-comparison claims are withdrawn; those frames do not support them. Original frames and publication history remain available. This narrow recheck does not rerun or extend the other desktop verdicts to the new head.

## Cleanup

Candidate removed after testing; no putgd or helper resident remains. dpkg reports residual configuration only (`rc 26.1114.5030~dev+geb3da9962dc8`), with no installed binary. Exact owned cover/input PIDs were ended. [Restoration log](restoration.txt). The k72 desktop lease was released **verified-clean**, with no leftovers: [receipt](release.json). No guest was used, no product code changed, no PR comment/issue/merge, and no subagent.

Setup attempts were bounded: an initial cover exited on stdin EOF; a subsequent input-holder inherited the SSH error stream; both were ended by their exact owned PIDs. The final cover precheck passed at 100% before any acceptance frame. The KWin helper needed its explicit documented D-Bus `ss` signature. Existing lab transport/RFB/control recipes were used; frames remain full, unmasked and uncropped.
