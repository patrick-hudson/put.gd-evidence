# Round-start baseline and final CI

The coordination file specifically requests a picture from the round-start
nightly,32a9a763e3502e0bf26db88def6140a7e250bbb4. Added
 a-round-before-final.png from that exact production source, compiled on f44
with the same SDK/Qt and displayed on Aurora's native Plasma/Wayland desktop
at Fit77%. This is additional to the current-nightly cdac6e4b3 before/after
pair, which isolates this fix from the separately merged editor tools.
The same thin covered-colour line appears at the left edge; arrow added with
production EditDocument/Commands. The toolbar differences between round start
and the after picture come from already-merged PR1369, not this fix.

The initial incremental round-start archive build was not used for pictures:
git archive restored old file mtimes. After that build completed, every changed
source path in tools/pg-round-changed.txt was touched and the picture target
rebuilt (tools/pg-round-rebuild.log). Both logs are retained. The corrected
command was: while IFS= read -r path; do test ! -f "$path" || touch "$path";
done < /tmp/pg-round-changed.txt; cmake --build --preset dev --target pg_round_picture.
The round picture driver uses QCoreApplication::exit directly, avoiding the
standalone discard-flow trap in the first pair. It exited normally. Its source
and binary hash are retained. The final f44 cache now holds this round-start
source/picture build; earlier tested binaries are identified by the original
manifest and commits, not by that cache's current contents.

Aurora lease02:12:14–02:12:54UTC, visibly idle before and after. Private runtime
session suffix remained30 UTF8 bytes, Wayland24, bus18 (all below107).
Exact scratch files/directories and copied binary removed after export;
clean release receipt aurora-round-release.json is retained.

Both final-head CI runs completed successfully:
- PR1378 /80ee533971e8aaa07063764abfb55043a6c88ba1:42739079215.
- PR1380 /04ee694dd2523652c06cc8f78560f1bd92e81981:42739839854.
Both Ubuntu24.04 and26.04 jobs and required CI summary pass. Unselected package,
PipeWire and sanitizer jobs are skipped by path selection; none is claimed run.
Complete CodeRabbit review bodies were read and checked for Outside diff range
comments (none); generic docstring warning answered. Final GraphQL sweep found
zero review threads on both PRs. Nothing merged; no PR watches or subagents.
