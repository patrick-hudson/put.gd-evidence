# Interleaved native hotkey tail study

A: nightly code baseline `466449a4c69a07a1997668d1b70d637abac76a16`. B: candidate `357210d2f1cb7b65f77166e34eb535d42e497fd0`, native DEB from CI43448444706. Physical m74 Cinnamon/X11,1920×1080,scale1.

**Neither p95-difference interval excludes zero.** The prior30-sample +15.82ms estimate is not reproduced by this larger controlled warm study. This does not establish equivalence or rule out an after-quiet cost: that point estimate is+6.65ms and its interval remains wide. No product change was made.

|Condition/build|n|p50|p90|p95|p99|max (ms)|
|---|---:|---:|---:|---:|---:|---:|
|warm/A|180|142.08|155.18|158.09|175.54|181.52|
|warm/B|180|142.01|154.96|157.87|176.97|177.86|
|quiet/A|30|137.16|156.49|158.84|168.76|168.76|
|quiet/B|30|144.95|156.99|165.49|166.14|166.14|

|Warm block, chronological|n|p50|p90|p95|p99|max (ms)|
|---|---:|---:|---:|---:|---:|---:|
|warm-00-A|60|142.91|154.67|157.36|165.74|165.74|
|warm-01-B|60|141.72|152.61|154.55|177.86|177.86|
|warm-02-A|60|141.07|155.49|157.76|181.52|181.52|
|warm-03-B|60|142.08|156.31|160.54|164.56|164.56|
|warm-04-A|60|142.26|153.80|162.68|175.54|175.54|
|warm-05-B|60|142.10|156.32|157.79|176.97|176.97|

|Candidate−baseline|Point ms|Bootstrap95% interval ms|Includes zero?|IID sensitivity interval ms|
|---|---:|---:|---|---:|
|warm p50|-0.07|[-2.30, +2.02]|**yes**|[-1.65, +1.95]|
|warm p95|-0.21|[-11.46, +5.56]|**yes**|[-9.66, +4.73]|
|quiet p50|+7.79|[-3.98, +13.23]|**yes**|[-3.91, +13.32]|
|quiet p95|+6.65|[-13.66, +15.46]|**yes**|[-11.77, +15.46]|

Methods: p50 is the median; other quantiles use nearest rank. All samples retained. Primary percentile bootstrap:10,000 replicates,seed1428; resample adjacent A/B block pairs and samples within each block. Warm has three pairs of60-sample blocks; quiet has30pairs of one observation. IID pooled resampling is supplied as sensitivity, not substituted for the paired analysis. No equivalence margin was specified.

Warm schedule A,B,A,B,A,B; fresh resident and five warmups per block,60 measured presses,3s spacing. Quiet schedule alternates build every press; each fresh resident gets five warmups then40s without session queries before one measured press. Exactly180warm and30quiet per build; warmup presses excluded.

## Where time and faults occur

|Condition/build|Map p50/p95|Drawable p50/p95|On-screen p50/p95 (ms)|Minor faults p50/p95|Major faults max|
|---|---:|---:|---:|---:|---:|
|warm/A|61.80/75.18|65.57/86.53|142.08/158.09|40/48|0|
|warm/B|62.92/77.43|67.35/82.96|142.01/157.87|40/45|0|
|quiet/A|60.31/84.97|64.88/88.53|137.16/158.84|186/193|0|
|quiet/B|64.70/81.35|71.40/90.45|144.95/165.49|191/197|0|

Cold median RSS before wait→before press: A32,666→8,168KiB; B33,066→8,178KiB. Every quiet interval is at least40.0001s. All60quiet observations show substantial RSS release; inspect per-press clean-page and RSS fields. Minor-fault median increases40→186(A),40→191(B); major faults remain0. Candidate incurs five more median minor faults after quiet. It shows a+4.39ms median mapping delay and+7.79ms median on-screen delay there, but the median and tail difference intervals both include zero. There is no resolved tail shift to attribute; mapping includes dispatch/adapter/helper startup and is not an isolated adapter-only clock. Release debug logs contain no finer internal timing lines; no instrumentation/fix was added.

Native resident executable file/mapped bytes: A11,260,112/9,228,288; B11,827,296/9,699,328. Increase567,184file bytes and471,040mapped bytes. No separate putgd-core DSO appears in these native maps; core code is part of the executable. Native QtCore6.4.2 is the same path and size for both:5,275,592file bytes/5,275,648mapped bytes. Full per-resident file inventories are retained; mapped virtual bytes are not resident-page counts.

## Controls and scope

Exact-owned selector PID/start/device/inode, inner white ring at102,151,4msroot readback; black outer ring checked separately. All selections cancelled. Frozen harness unchanged. The covering canvas changed from managed feh to an owned override-redirect X11 window after the feh canvas failed pixel admission. No compositor settings changed. Both builds use the same new fixture; **do not pool or directly compare these absolute times with the earlier managed-feh30-sample campaign**. The measured selector and timing/ownership witness are real. Failed canvas and missing-local-output-directory attempts have zero accepted samples and remain in the record.

Each block records quiet-host load/idle samples. Native is the scope of this follow-up; optional AppImage study was not run. No other build/scoring job competed onm74. No source changes, new tests, newissue or PR. No native package mutation. Cleanup passed; lease released18:12:26UTC, unrelated shared SSH jobs left intact.

[Structured analysis](analysis.json), [raw per-block data](data), [as-run driver](h1428-run.py), [witness](h1428-witness.py), [analysis program](h1428-analyse.py), [cleanup](cleanup.json).

Quiet-host checks: CPU idle 73.43–100.00%; one-minute load 0.00–2.70,four CPUs. Smallest quiet RSS drop 22784KiB.
