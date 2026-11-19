# Scroll capture: pinned side columns drawn once (#1538)

What was tested: the scroll tracker's new painting rule (paint only what is proved to be the
page; draw what stays on the screen once), on the branch `fix/scroll-pinned-columns` at
commit `cd64fe8d6` (one commit on nightly `faf34a8c6`).

## Pictures

Each picture puts nightly's tracker (left) beside this branch's (right), replaying the
same recorded frames.

- `wikipedia-chrome-contents.png`, `wikipedia-chrome-end.png`: Wikipedia "Linux" in Chrome,
  a person scrolling, recorded live on aurora-amd (Aurora, Plasma 6.8.2 Wayland) with the
  frame tee. Nightly leaves the contents column in pieces and pieces of it at the page's
  end; this branch draws it once, whole.
- `mdn-firefox-columns.png`, `mdn-firefox-end.png`: MDN's `position` page in Firefox,
  steps of 600 px, from the 160-sequence corpus. Nightly repeats both side columns in
  every screen and leaves the contents column in pieces at the end; this branch draws
  them once, at the top.
- `github-firefox-screenshot.png`: a GitHub pull request in Firefox, steps of 600 px,
  from the corpus. Nightly cuts the sticky header's white into a dark screenshot; this
  branch keeps it whole.

## Results

- Synthetic scenes (`test_scroll_tracker`): 43 of 43. Session tests (`test_scroll_session`):
  68 of 68. Built with the dev preset on k72.
- Corpus (160 recorded sequences, `scroll_tracker_score.py --derived`, both browsers, on
  d69): 0 wrong placements (nightly 0); 17,105 frames placed and 338 skipped (nightly 17,103 and 343); 26,667 bands equal to the reference (nightly 26,691: the reference counts MDN's side columns as page in every screen, which this branch no longer repeats).
- Live on aurora-amd: Wikipedia "Linux" and the Al Jazeera article
  (`un-says-25-seafarers-killed-in-around-hormuz-since-february`) in Chrome and Firefox,
  with a person's scrolling and auto-scroll; React's `useState` reference and Microsoft
  Learn's WSL install page in both browsers (auto-scroll); Python's `stdtypes` page in both
  browsers up to the 60,000 px cap. Every run ended `done` or `end_of_content`. The live
  runs used lab builds of this branch from the last rounds before the final commit; the
  runs recorded with the frame tee (Wikipedia and the Al Jazeera article in Chrome,
  Wikipedia in Firefox with a person scrolling) were replayed with the final commit's
  tracker for the pictures and numbers here. Chrome on the Al Jazeera article under
  auto-scroll still skips most frames (a known limit before this change); with a person's
  scrolling, replaying the same frames, nightly placed 160 frames and skipped 104; this
  branch placed 192 and skipped none.
