# PR #1512: detail-pane fix re-check on m74

Both requested rows PASS on the physical Linux Mint 22.3 Cinnamon/X11 desktop, with a light theme and 1100×700 History window. The native display remained visible on the wall. No product code was edited.

## Exact build and CI

[CI run 43570460597](https://github.com/patrick-hudson/put.gd-desktop/actions/runs/43570460597) was watched in the foreground to completion using `gh run watch 43570460597 -R patrick-hudson/put.gd-desktop --interval 60`. Every job passed, including required CI. Installed its release-native-ubuntu24.04 DEB, package `26.1114.4983~dev+g62a5f8c65233`.

Installed `putgd-cli diagnostics` reported clean build commit `62a5f8c65233d5313b9838d4b33aa9de750b5002`, tree `62930adba877f63b0060c5cb639ac77faa02c8d7`, matching `git -C /home/patrick/work/put.gd-i1496 rev-parse 62a5f8c65^{tree}`. The test used a fresh private resident and XDG profile at `/tmp/l1512r`, with the lab keychain reference and isolated lab destination. Session socket 38 UTF-8 bytes, bus 18, X11 socket 17: all passed the 107-byte preflight. No Proton session was printed or exported.

## Results

1. **PASS.** Private synthetic upload, recovered running create journal, no retained local copy. Recovery reports unknown/create, linkFinishable true. Before the actual pointer click, row text was **Share link not finished**, its inline button **Finish share link**, and the pane read **Share link not finished. No local copy is available. You may still be able to download the uploaded image from its destination.** Clicked the row's button with xdotool at desktop coordinates 1050,418. Completed/shared, link present, clipboard matched, one item, exactly one Upload attempt. Logs show inspect/private then create/shared. Afterwards the row reads **Shared link**; pane reads **Uploaded · Shared link. No local copy is available…** and displays the link.
2. **PASS.** Originally shared synthetic upload, recovered running create journal, selected the exact item and invoked `ui.history {action:finishShareLink}`. Completed/shared, exact same URL as before recovery, clipboard matched, one item and exactly one Upload attempt. Sharing log sequence is original create/shared then retry inspect/shared, with no second create.

Pictures were annotated through put.gd's own editor (editor.open/apply/saveCopy/cancel), with #D7263D rectangles, arrow and short label: [before](before.png), [after](after.png).

Additional observation for the implementation owner: after successful completion, the bottom feedback strip still says **Finishing share link**, while row and pane already confirm Shared link. This stale feedback is visible in after.png; it does not change the two requested row/pane and duplicate-upload results above. This re-check does not establish whether it predates the fix.

## Retention and cleanup

Reused the first run's scripts after verifying archive SHA-256 `109d71ace3c584d02cc409f19f96efa92cb22b80a08ee0c42a94d5620cea277b` on both machines. New private attempts, raw logs and scripts are retained as `/tmp/p1512r-private.tar.gz` on m74 and workstation, with matching SHA-256 `db1914745e7f22edca9de656e38e108d390018b6b653ecbef8f7bfc1a8209326`. They exclude configuration and full diagnostics. Rejected search parameter and corrected pointer search/selection are retained; an initial wrong-selection after picture was preserved. First cleanup skipped the stopped Unix socket; corrected cleanup unlinked it explicitly, then removed empty runtime directories. Local final publish directory contains only these new pictures and this README.

Stopped only the exact resident PID. Removed exactly putgd using apt, with no autoremove; dpkg reports deinstall ok config-files. No installed app processes remained. Private config/data/state/cache/runtime and diagnostics were removed by individual unlink and empty-directory removal. Both leases released with --verified-clean: desktop 2026-11-14T07:39:01Z, Proton 07:39:09Z. Final status --check reports free; pre-existing shared SSH PIDs 313646 and 313651 were preserved. Host release receipts are under ~/putgd-lab/locks/history/. The two synthetic uploads remain in the isolated lab account by design.
