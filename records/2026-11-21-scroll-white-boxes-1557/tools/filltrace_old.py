# filltrace_old.py FILE: the fill tracer for the re-check's tracker (54c5281ac, before #1672).
import sys
p = sys.argv[1]
s = open(p).read()
def rep(old, new):
    global s
    assert s.count(old) == 1, (old, s.count(old))
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
rep("  for (const FrameCopy* copy : {&topCopy_, &bottomCopy_})\n    for (int y = 0; y < height_; ++y) {",
    "  g_phase = \"holefill\";\n  for (const FrameCopy* copy : {&topCopy_, &bottomCopy_})\n    for (int y = 0; y < height_; ++y) {")
rep("  const uint32_t page = pageColour_;", "  g_phase = \"plain\";\n  const uint32_t page = pageColour_;")
rep("      c = e;\n    }\n  return totals_;\n}\n\n}  // namespace putgd::scroll", "      c = e;\n    }\n  if (g_fill) std::fflush(g_fill);\n  g_phase = \"compose\";\n  return totals_;\n}\n\n}  // namespace putgd::scroll")
if '#include <cstring>' not in s:
    s = '#include <cstring>\n' + s
open(p, 'w').write(s)
print('old filltrace patched')
