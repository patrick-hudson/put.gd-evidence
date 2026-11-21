# Scrolling capture: the region's bottom-edge line stays out of the page (#1796)

Evidence for [PR #1813](https://github.com/patrick-hudson/put.gd-desktop/pull/1813), which fixes
[#1796](https://github.com/patrick-hudson/put.gd-desktop/issues/1796). On Cinnamon, Firefox's page ends one row above the
selected region, so every frame's last row is a dark line, and pieces of it were written into the page as stray lines.

`pictures/q4-edge.png`: m74 run `firefox-github-user-q-4` (from the #1557 record `2026-11-21-scroll-white-boxes-1557`),
every recorded frame replayed through nightly `4030f0330` and through the PR's first head `17ecb42a5`, next to Firefox's
full-page picture at image row 24,795. Nightly draws the edge line across the table row and the white margin; the PR doesn't.

Live acceptance on the candidate packages is added to this record when it has run.
