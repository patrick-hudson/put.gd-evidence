# celltrace.py FILE: on top of a fill tracer: env CT="ROW0,ROW1,X" logs every
# write covering pixel column X in page rows [ROW0, ROW1] as
# "W frame phase row x0 x1 lum" to the FILLTRACE file (frame = addFrame count).
import sys
p = sys.argv[1]
s = open(p).read()
def rep(old, new):
    global s
    assert s.count(old) == 1, (old, s.count(old))
    s = s.replace(old, new)
rep("static std::FILE* g_fill = nullptr;\n", "static std::FILE* g_fill = nullptr;\nstatic long long g_frame = -1;\n")
rep("""  if (std::strcmp(g_phase, "compose") != 0) {""", """  {
    static long long c0 = -2, c1, cx;
    if (c0 == -2) { c0 = -1; const char* e = std::getenv("CT"); if (e) std::sscanf(e, "%lld,%lld,%lld", &c0, &c1, &cx); }
    if (c0 >= 0 && row >= c0 && row <= c1 && x0 <= cx && x1 > cx) {
      if (!g_fill) { const char* e = std::getenv("FILLTRACE"); g_fill = e ? std::fopen(e, "w") : stderr; }
      const uint8_t* q = bgrx + (cx - x0) * 4;
      std::fprintf(g_fill, "W %lld %s %lld %d %d %u\\n", g_frame, g_phase, row, x0, x1, (q[0] + 2u * q[1] + q[2]) / 4);
    }
  }
  if (std::strcmp(g_phase, "compose") != 0) {""")
rep("TrackResult ScrollTracker::addFrame(const FrameView& frame, TrackerHint hint) {", "TrackResult ScrollTracker::addFrame(const FrameView& frame, TrackerHint hint) {\n  ++g_frame;")
open(p, 'w').write(s)
print('celltrace patched')
