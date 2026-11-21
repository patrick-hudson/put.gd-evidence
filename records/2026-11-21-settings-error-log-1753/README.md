# Settings error log and History's deletion notice (#1753, PR #1756)

Desktop acceptance of PR #1756 head `ec3ef537aa6262e7895904657be246f3f3a57653`, using the
AppImage that PR CI run 44856584833 built from it (`26.1121.5968-dev+gc5d986f2a16c`,
merge commit `c5d986f2a16ca14572f7e3b6ce160a7d0a1c0572`, tree `b8f7cb3cc8460a97e788f716412c42bd11414498`;
the resident's `diagnostics.build` reported the same commit and tree).

Host: aurora-amd, physical Aurora Fedora 45, Plasma 6.8.2 on Wayland, under the desktop
lock (session `errlog-1753-b`, released clean). The resident ran with private XDG folders on
the real session. The destination was an S3 destination ("Work S3", bucket `putgd-shots`) on
`tests/fixtures/s3_server.py` on loopback, with the fixture's published synthetic key pair
saved in the session keyring (keychain mode) and removed afterwards. Frames come from the
host's loopback VNC; clicks are real pointer input through `tools/lab/rfb.py`. The pictures
were annotated with put.gd's own editor (`editor.open`/`editor.apply`/`editor.saveCopy`).

Patrick's case reproduced: upload a file, restart put.gd with "Unlock saved credentials when
put.gd starts" off, so the saved credentials are not loaded, then Delete from destination.

| Picture | What it shows | Result |
| --- | --- | --- |
| `1-history-deletion-notice.png` | The deletion fails with `credential_setup_required`. History's notice names the file and its destination, offers Open error log and ×, and clears after 12 s; the inspector offers Unlock saved credentials beside Retry deletion | Pass |
| `2-error-log-entry.png` | Open error log opens Settings → Error log on that entry: the row, the full message, code, deletion outcome, IDs and the next steps as buttons | Pass |
| `3-error-log-resolved.png` | Unlock saved credentials loaded the keychain item ("Credentials loaded. Choose Retry deletion"), Retry deletion removed the object, and the entry turned Resolved with its resolution, still listed | Pass |
| `4-history-after.png` | Show in History opens the item, now "Deleted from destination"; no old error is kept on History's bottom line | Pass |

An earlier rehearsal on the same host with the PR's previous head showed the same flow and
one flaw, "Remote deletion accepted…" left on the status line when the outcome arrives on the
first poll; it is fixed in this head, as picture 1 shows.
