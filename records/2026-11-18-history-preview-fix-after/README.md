# Expanded history preview with the fix, under an empty work area

Picture for PR #1626 (issue #1625). A private resident of a build of commit `a190ece96` (the PR's head) on m74
(Linux Mint 22.3, Cinnamon X11, Qt 6.4), two desktop captures in History, the first item selected with `ui.history`
`select`, `_NET_WORKAREA` set to `0, 0, 0, 0`, then `ui.history` `expandPreview`. The preview is 932x651 and shows
its picture, and `putgd-ui` logged no `Negative sizes` warning. The same tree with the change reverted gave 150x145
and two warnings. The marks were drawn with put.gd's headless editor (`editor.apply`, `editor.saveCopy`).

The before-pictures are in `2026-11-18-history-preview-empty-workarea`.
