# Scrolling capture: white boxes over words in one live GitHub run (Cinnamon)

One of six package runs on m74 (Linux Mint 22.3 Cinnamon X11, Firefox, GitHub PR #1398, "you scroll") for PR #1821's
acceptance showed flat writes over page text. The run is `firefox-github-user-turn-2`; the candidate package is
`26.1122.6221~dev+g09930ec2c902`, which is nightly `c4cee700b` plus #1821's tracker change.

`pictures/turn2-capture-vs-reference.png`, rows 13,468-13,528 and 37,352-37,412, x 400-1,400, capture above Firefox's own
full-page picture for each. At 13,488 a text line ("is also exact.") is cut by about half its height. At 37,372 white
boxes cover words ("complete/…/h…ial"). The capture ended `done`, full height, with 66 frames skipped (`result.json`).

The run has no frame tee, so it cannot be replayed. On the two tee'd runs made right after with the same tracker, and the
7 earlier recordings, nightly and #1821 replay pixel-identical. #1821's rule only changes the place of a frame that turns
back more than half a screen, and it does not touch writing. The defect comes from code shared with nightly.
