# Shortcut recording accessibility on Mint Qt 6.4.2

PR #1257, issue #862. Source head `850cb39f0016ac7e10ec7093b88d36a6e347397c`, clean CI-built Ubuntu 24.04 DEB `26.1107.4055~dev+g850cb39f0016`, from [CI run 42410618871](https://github.com/patrick-hudson/put.gd-desktop/actions/runs/42410618871), artifact `release-native-ubuntu24.04` (13589413653). No compilation on Mint. Package SHA-256 and runtime manifest are in cleanup.json.

Physical m74 (192.168.68.74), Linux Mint 22.3, Cinnamon/X11, distro Qt 6.4.2. Native wall VNC tile at workstation port 5974 stayed visible. Lock session worker-c-862 ran 20:33:31–20:36:58 UTC on 2026-11-07. See launch.json, cleanup.json and lock-release-final.json for exact session, PIDs and host versions.

The raw D-Bus probe queried only the owned putgd-ui PID, never libatspi/pyatspi or Cache.GetItems. Stable accessible name remained `Shortcut recording status`. Actual exported Description values were:

- Ready: `Press shortcut… Release all keys to keep it. Escape cancels.`
- Recorded, after real VNC Ctrl+1: `Ctrl+1 recorded. Changes save automatically.`
- Canceled, after a second recording and real VNC Escape: `Recording canceled. The draft shortcut is unchanged.`

The three status JSON files retain the exact accessibility bus/path/PID and exported descriptions. m74-ready.png saves the visible recording state; m74-before.png and m74-cleanup.png save the idle desktop before/after. This fixes accessibility only; no changed visible pixels are claimed.

The new SettingsGui::shortcutRecordingExportsEveryStatusThroughAccessibility test passed on Ubuntu 24.04 in the linked CI run. That GUI regression additionally covers preparing, pending chord, clear, unsupported key, overlapping second key, asynchronous preparation failure, cancel/restore failure and ignored superseded callbacks. The retained CI flake ledger records a first-attempt full-suite pass. These additional failure states were not induced on the physical desktop.

Initial probe attempts are retained as context: the first script used a dbus-python convenience method unavailable on BusConnection (AttributeError); it was corrected to the bus daemon's GetConnectionUnixProcessID. With accessibility initially disabled the first app exported only its root. IsEnabled was enabled without ScreenReaderEnabled, and the owned app was restarted with QT_LINUX_ACCESSIBILITY_ALWAYS_ON=1. A name-only Shortcuts query was ambiguous because hidden pages also have that name; the visible sidebar was selected through VNC, then the uniquely named recording action was invoked over raw D-Bus. No status was inferred from pixels. Both initial and corrected private socket paths were calculated as 42 bytes before launching and were below 107 bytes (launch preflight.json; socket-check.json independently repeats the check).

Cleanup: both owned app families exited through ui.quit; all four exact PIDs were absent. IsEnabled was restored to false. The CI test DEB was removed without autoremove, as required by the desktop lease inventory; the previous lab package had been 26.1104.3851~dev+g6d67545ca87c. A separate #1187 campaign process appeared during the lease; PID 2999831 was left alone and named explicitly with --not-mine in the successful release receipt. No logout or compositor restart occurred. Private synthetic profiles remain under /tmp/c862flxkbc52 and /tmp/c8625wrj3__3 on m74 for investigation; no user destination or credentials were used.
