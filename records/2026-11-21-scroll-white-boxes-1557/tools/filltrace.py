# filltrace.py SRC_COPY/src/core/ScrollTracker.cpp: lab-only tracer (#1557).
# Every span written by finish() goes to the file in env FILLTRACE as
# "phase row x0 x1" (phases: flush = flushPending at the end, overlay = pinned
# parts drawn once, holefill = first/last screen's own pixels in holes,
# plainvote = voted plain cells (no write), plain = the flat-colour fill).
import sys
p = sys.argv[1]
s = open(p).read()
def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (old, s.count(old))
    s = s.replace(old, new)
rep("namespace putgd::scroll {", "namespace putgd::scroll {\nstatic const char* g_phase = \"compose\";\nstatic std::FILE* g_fill = nullptr;\n")
rep("void MemoryCanvas::writeSpan(long long row, int x0, int x1, const uint8_t* bgrx) {",
    """void MemoryCanvas::writeSpan(long long row, int x0, int x1, const uint8_t* bgrx) {
  if (std::strcmp(g_phase, "compose") != 0) {
    if (!g_fill) { const char* e = std::getenv("FILLTRACE"); g_fill = e ? std::fopen(e, "w") : stderr; }
    std::fprintf(g_fill, "%s %lld %d %d\\n", g_phase, row, x0, x1);
  }""")
rep("TrackTotals ScrollTracker::finish() {", "TrackTotals ScrollTracker::finish() {\n  g_phase = \"flush\";")
rep("  overlay(topCopy_, true);", "  g_phase = \"overlay\";\n  overlay(topCopy_, true);")
rep("  for (const FrameCopy* copy : {&topCopy_, &bottomCopy_}) {\n    const bool topSide = copy == &topCopy_;",
    "  g_phase = \"holefill\";\n  for (const FrameCopy* copy : {&topCopy_, &bottomCopy_}) {\n    const bool topSide = copy == &topCopy_;")
rep("      if (store_->level(p, c) == 0 && store_->plain(p, c)) store_->set(p, c, 1);",
    "      if (store_->level(p, c) == 0 && store_->plain(p, c)) { store_->set(p, c, 1); if (!g_fill) { const char* e = std::getenv(\"FILLTRACE\"); g_fill = e ? std::fopen(e, \"w\") : stderr; } std::fprintf(g_fill, \"plainvote %lld %d %d\\n\", p, c * opts_.cellPx, (c + 1) * opts_.cellPx); }")
rep("  const uint32_t page = pageColour_;", "  g_phase = \"plain\";\n  const uint32_t page = pageColour_;")
rep("  return totals_;\n}\n\n}  // namespace putgd::scroll", "  if (g_fill) std::fflush(g_fill);\n  g_phase = \"compose\";\n  return totals_;\n}\n\n}  // namespace putgd::scroll")
if '#include <cstring>' not in s:
    s = '#include <cstring>\n' + s
open(p, 'w').write(s)
print('filltrace patched')
