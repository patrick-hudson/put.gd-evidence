# Settings stays unsaved after a restored checkpoint, a finished rename and a daily-check toggle (#1735)

Annotated before/after pictures for put.gd-desktop issue #1735 and its fix pull request, taken on a real desktop, with
the scripts, the unannotated crops and the run logs.

## What was tested

- **Host:** m74, Linux Mint 22.3, Cinnamon on X11 (1920x1080), the physical desktop, under the desktop lock (owner
  `fix1735`, session `mcp-fix1735`); the build and the annotation held the quiet lease. Every lock was released with the
  cleanup check. No process of these runs was left and `/run/user/1000/pg1735` was gone after each run.
- **Before:** the `putgd` 26.1125.7045~nightly package already installed on m74 (commit
  `9d9f65eb8f7c4e9a7eddaf8b0c7938b95e805d40`), run from `/usr/bin` and left as it was found. It contains #2040 and has the
  same `src/ui` as the fix branch's base.
- **After:** the fix branch `fix/settings-unsaved-1735` at `ce38caefd39e6b1d6704c5a4907463e95d172c90` (tree
  `c89164aeb26ae512f01e6664ac20670c0785e01f`), copied to m74 without `.git` and built with `cmake --preset dev` (targets
  `putgd`, `putgd-ui`, `putgd-cli`), so it reports `0.0.0-dev.unknown`.
- **Run** (`tools/capture1735.py`): a private resident of the build (own `XDG_*` folders and runtime folder) on the real
  display. The development template adds one S3 destination (nothing is uploaded; no credentials). Upload clipboard
  goes to no destination and a local copy is kept. The configuration file is edited to have no Updates object, then
  reloaded. Steps:
  1. Destinations: the destination's name is retyped as "Team photo". 0.4 s later, before the 600 ms typing pause
     would send it, this run's own `putgd-ui` process is killed, so the resident keeps the checkpoint taken mid-rename.
     The configuration's revision is unchanged (`after kill ... sameRevision: True` in the logs).
  2. Settings opens again and restores the checkpoint. The rename is finished with one more letter and Tab, and is
     saved as "Team photos".
  3. Settings → General: daily update checks are turned off, then on again.
  4. Upload clipboard in the command band.
- **Annotation:** put.gd's own editor in a private headless resident of the "after" build (`tools/annotate-run.sh`,
  `tools/annotate1735.py`, `tools/spec.json`). The crops are the put.gd window only (`tools/crop1735.py`).

## Result

| # | Build | Picture |
| --- | --- | --- |
| 1 | Before (nightly 7045) | ![](1-restored-before.png) |
| 2 | Before (nightly 7045) | ![](2-refused-before.png) |
| 3 | After (fix build) | ![](3-renamed-after.png) |
| 4 | After (fix build) | ![](4-upload-clipboard-after.png) |

1. The restored window shows the name typed before the window process ended.
2. Nightly 7045: after the rename and the daily check off and on, the file holds `"updates": {}`
   (`updates after click {}` in `before-capture.log`). Upload clipboard is refused with "Some changes in Settings aren't
   saved yet. Finish or undo them, then try again.", while the window's status line still says "Settings save
   automatically".
3. Fix build: the same checkpoint is restored and the finished rename is saved.
4. Fix build: Upload clipboard runs. The text is kept as a local copy and a History record is written.

**Limit:** the daily-check control exists only in tagged package builds. An untagged build shows "This build wasn't
made by a put.gd package" instead, so the fix build couldn't run step 3 on the desktop. The offscreen test
`gui_settings_destinations` → `restoredRenameThenUpdatesToggleEndsSaved` covers that step: it fails without the fix at
"daily check back on" and passes with it. Pictures of step 3 with the fix will be added to this record from the first
nightly that contains it.

The "Action failed: The window could not be opened" banner in the uncropped frames comes from killing `putgd-ui` in
step 1. It is outside the crops.
