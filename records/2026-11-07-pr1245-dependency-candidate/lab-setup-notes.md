# Lab setup notes

Package downloads ran on the builders, using `gh run download 42363534641` with repository and named artifact arguments. No package was downloaded to the workstation and no candidate was compiled. GitHub authentication was supplied only in memory through stdin/environment; no credential was written into a command or evidence.

The d69 unattended read-only GitHub token could download the CI artifacts. The other four builders had no `gh` command on their initial PATH. Standard distro `gh` packages were installed on f44, k72 and m74; Aurora used `gh` installed inside its existing Fedora 45 `putgd-build` Toolbx. No broad upgrade, removal or reboot was requested. Fedora's installation output reported: “Pending offline transaction has been invalidated.” That package-manager side effect is retained here; the acceptance run did not reschedule any system upgrade.

An initial d69 download put two different native artifacts in one directory and `gh` refused to overwrite their common build-info.json. That attempt was preserved in c1245. The corrected directories under c1245b separate the Ubuntu 26.04 and Debian 13 artifacts. Their DEB filenames are identical but their SHA-256 hashes differ; the native package platform and digest are recorded separately.

All workstation source edits for the acceptance controllers were private under /tmp/pg1245. The shared checkout's existing untracked b1-gnome.log and docs/plans/ were left untouched. No source branch switch or commit was made there.
