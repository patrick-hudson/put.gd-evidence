# Expanded history preview shrinks to a 150x145 box when the screen reports no work area

Found by the on-screen GUI fuzzer on a Linux Mint 22.3 Cinnamon X11 guest (2 monitors, monitor modes changing),
nightly `26.1117.5114`, DEB for Ubuntu 24.04. The fuzzer hit it twice (seeds 306 and 310; the JSON files are its
findings with the last 60 actions). Both times the History window's expanded preview dialog was 150x145 and
`putgd-ui` logged `QWidget::setMinimumSize: (historyExpandedImage/QLabel) Negative sizes (-396,-161) are not possible`
(`-257,-161` the second time).

## Reproduction on a fresh guest

1. Fresh `cinnamon-x11` overlay, the nightly DEB, two desktop captures so History has two images.
2. History, select the first item, click its preview: the dialog is 932x426 and shows the picture
   (`before-normal-workarea.png`).
3. Close it, then make the screen report an empty work area, which is what Cinnamon does for a moment while it
   re-lays out its outputs: `xprop -root -f _NET_WORKAREA 32c -set _NET_WORKAREA "0, 0, 0, 0"`.
4. Click the preview again: the dialog is 150x145 with no picture and the log line above appears
   (`before-empty-workarea.png`; this run logged `Negative sizes (-515,-161)`).

Cause: `HistoryWindow::expandPreview` takes the screen's available size minus 48 px and the dialog's margins as its
limit without a floor, so an empty area gives a negative limit and a negative minimum size.
