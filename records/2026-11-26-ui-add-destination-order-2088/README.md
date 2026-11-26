# Add destination and Storage service menu order (#2088): before and after pictures for PR #2092

Before and after pictures of **Destinations → Add destination** (dark and light themes) and **Destination actions (⋯) → Storage service** (dark theme) for [put.gd-desktop#2088](https://github.com/patrick-hudson/put.gd-desktop/issues/2088) and [PR #2092](https://github.com/patrick-hudson/put.gd-desktop/pull/2092).

## Host and builds

- **Host:** `m74` (`192.168.68.74`, Linux Mint 22.3 Cinnamon X11, physical `:0`, visible on Patrick's display wall)
- **Before build (merge base):** `c35651f28b68418b7d328f1a412919c772174c80` (`26.1126.7127-dev+gc35651f28b68`, Release, `dirty: false`)
- **After build (PR #2092 head):** `dbcc155d553f2a0a22b5b513f3b8617abed1a46d` (`26.1126.7128-dev+gdbcc155d553f`, Release, `dirty: false`)
- **Desktop lock release receipts on `m74`:**
  - Build quiet lease: `/home/patrick/putgd-lab/locks/history/2026-11-26T03-55-06Z-quiet-release.json`
  - Capture desktop lock: `/home/patrick/putgd-lab/locks/history/2026-11-26T04-00-04Z-release.json`
  - Annotation desktop lock: `/home/patrick/putgd-lab/locks/history/2026-11-26T04-02-42Z-release.json`

## Method

1. Built clean Release binaries (`putgd`, `putgd-ui`, `putgd-cli`) on `m74` for both `c35651f28` and `dbcc155d5`.
2. Ran private residents (`XDG_RUNTIME_DIR=/run/user/1000/pg2088`, 40-byte socket path) on `m74`'s `:0` display under `tools/lab/desktop_lock.py run m74 --release`, with one synthetic S3 destination (`Example S3`, `example-captures`, no credentials).
3. Captured full desktop frames with `import -window root` (`frames/`), cropped each before/after pair to identical coordinates (`crops-unannotated/`), and annotated the crops using put.gd's own image editor (`editor.open`, `editor.apply`, `editor.saveCopy`, `editor.cancel` via `scripts/annotate2088.py`).

## Pictures

| Surface | Before (`c35651f28`) | After (`dbcc155d5`) |
| --- | --- | --- |
| **Add destination** (dark) | `1-add-destination-dark-before.png` | `1-add-destination-dark-after.png` |
| **Add destination** (light) | `2-add-destination-light-before.png` | `2-add-destination-light-after.png` |
| **⋯ → Storage service** (dark) | `3-storage-service-dark-before.png` | `3-storage-service-dark-after.png` |
