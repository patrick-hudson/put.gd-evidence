# Page metrics — k72

These are measured raw comparisons, not blanket passes. Read README.md for page-layout changes, caps, geometry and known limits. Bands are equal/total tolerant 64-row bands; 0/0 is unproved. Seconds per 10,000 px uses the capture elapsedMs and saved height (not wall time). User mode must be done and non-truncated; AUTO may reach its height cap. FPS is the actual helper source rate.

| Case | End; height/document | Bands | Placed/skipped | FPS | s/10,000 px | Fresh/Done-added |
|---|---|---:|---:|---:|---:|---|
| firefox-wiki-auto | end_of_content; 24115/24117 | 377/377 | 834/0 | 35.3 | 28.558 | 1 fresh; 0 added |
| firefox-wiki-user | done; 24115/24117 | 377/377 | 293/0 | 35.6 | 12.799 | 1 fresh; 0 added |
