# Expanded history preview, round 2 of PR #1626: work area, then screen, then a fixed default

Build of the PR's second head on m74 (Linux Mint 22.3, Cinnamon X11, Qt 6.4.2). A private resident, two desktop
captures, the first History item selected and expanded through `ui.history` (`select`, `expandPreview`), with
`_NET_WORKAREA` set to the value named in each picture. Both previews are 932x651 and show their picture, and
`putgd-ui` logged no `Negative sizes` warning. The marks were drawn with put.gd's headless editor.

- `after-empty-annotated.png`: `_NET_WORKAREA` `0, 0, 0, 0`. The first head's build gave 150x145.
- `after-strip-annotated.png`: `_NET_WORKAREA` `0, 0, 1920, 48`. The preview is sized from the screen's geometry.
- `old-vs-new-sizes.txt`: the sizes the old and new rules give on the screens that went wrong, and the unit test
  result with each rule.
