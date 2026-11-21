# Error log: Remove from History only for a removed destination (#1760)

What was tested: Settings → Error log offers **Remove from History only** on an entry whose
code is `destination_removed`, opens History's own deletion dialog for the file, removes the
History record when confirmed, and marks the entry resolved. The uploaded file stays on the
server.

- Host: aurora-amd (Aurora Fedora 45, Plasma 6.8 Wayland), the real desktop session, under the
  aurora-amd desktop lock (released clean at 2026-11-21T06:23Z).
- Build: dev build (Toolbx `putgd-build`) of put.gd-desktop `20cbc1fb2` on branch
  `fix/deleting-removed-destination` (nightly `0d6eb84cf` merged in). The window reads
  `0.0.0-dev.unknown` because the tree was synced without `.git`. The pushed head adds only an
  `errors.act` check for an item that is already gone.
- Resident: private profile (`XDG_*` under `~/work/errlog-1753/acc60`, runtime
  `/run/user/1000/pe60`), driven over its session socket by `tools/acc60.py`.
- Destination: the loopback custom-uploader fixture (`tests/fixtures/http_uploader_server.py`,
  no token, imported as a `.sxcu` with session credentials). Synthetic image; nothing left the host.

Steps: upload `quarterly-chart.png`; remove the destination in Settings (`settings.patch`);
`delete.confirm` is refused with `destination_removed`, which the error log records with
next steps `remove_from_history` and `show_in_history`; select it in Settings → Error log
(picture 1); press Remove from History only (picture 2, History's dialog); confirm (picture 3).

Results:
- After confirming, `history.list` had no records, the fixture still held the file
  (`deleted: false`), and the entry was resolved with "Removed from History".
- A second run through the production `putgd-cli errors.act {"action":"remove_from_history"}`
  answered `method: history.forget`, `removed: 1`, and resolved its entry. Repeating it
  answered `history_not_found` without adding a log entry (3 entries before and after).
- Pictures annotated with put.gd's own editor (`editor.open`/`apply`/`saveCopy`) using
  `tools/annotate60.py` and the `tools/spec-*.json` files.
