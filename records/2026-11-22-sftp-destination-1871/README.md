# SFTP destination Settings panel (#1871)

Offscreen renders of the new **SFTP** destination in Settings → Destinations, from `putgd-ui-catalog` built on f44 (Fedora 44, Qt 6.11.2) at put.gd-desktop commit `6ac10aa48cec8fff52470a1ef8cf0cbf74be1f57` (branch `feat/sftp-destination`). The catalog shows a fixed synthetic version string; the build is that commit. Server, user and host key are synthetic.

- `settings-sftp.png`: `sftp://alice@files.example.com:2222/srv/www/shots` pasted into Server fills Server, User and Folder on server. The line under them is what `ssh -G` resolves (the catalog's stand-in answers for ssh). The destination list says "Ready to test".
- `settings-sftp-trust-key.png`: a test that met an unknown host key offers **Trust key**. The fingerprint is on its own line, and Trust keeps only that exact key.

The catalog's secret-control states still match `tools/lab/surface_driver/secret-states.json` (37 states). Real-server results are in the PR: the opt-in live test passed 8/8 against the storage lab's OpenSSH server on aurora-amd.
