# Issue 1428 corpus index

174 checked Capture region images across m74, d69, f44, k72, Budgie/labwc and Hyprland, all on published nightly 26.1112.4660. Each has seven classes at light/dark and 100%/125%, plus one dense region. Every class exceeds 200 words per desktop. Character counts and font pixel sizes are recorded per capture.

Download this record and the six sibling records named in records.json, preserving their relative paths. Run score.py on this manifest to score the entire fixed corpus offline for one engine build. Each source record holds its separately measured distribution baselines; these are not pooled engine quality results. coverage.json validates corpus completeness and hashes, not recognition quality. Full monitors are 1920x1080; the 4K gate is open. Feature memory, clipboard, phase latency and candidate acceptance are not claimed.
