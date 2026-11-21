# whytrace.py FILE (after filltrace + celltrace): env WHY="ROW,CELL" logs, for
# page row ROW and cell column CELL, every decision about it to the FILLTRACE
# file: P = proof test (compose step 1), Q = pending capture (step 3),
# F = flushPending (written as seen / vote).
import sys
p = sys.argv[1]
s = open(p).read()
def rep(old, new):
    global s
    assert s.count(old) == 1, (old, s.count(old))
    s = s.replace(old, new)
rep("static long long g_frame = -1;\n", """static long long g_frame = -1;
static long long g_whyP = -2; static int g_whyC = 0;
static bool whyOn() {
  if (g_whyP == -2) { g_whyP = -1; const char* e = std::getenv("WHY"); if (e) std::sscanf(e, "%lld,%d", &g_whyP, &g_whyC); }
  if (g_whyP >= 0 && !g_fill) { const char* e = std::getenv("FILLTRACE"); g_fill = e ? std::fopen(e, "w") : stderr; }
  return g_whyP >= 0;
}
#define WB(x) int(((x) >> (g_whyC & 63)) & 1)
""")
# A: proof test
rep("""        const uint64_t alreadyVer = store_->ver[at + size_t(w)];
        uint64_t need = ~(alreadyVer | blockedMask) & full[size_t(w)];""",
"""        const uint64_t alreadyVer = store_->ver[at + size_t(w)];
        if (whyOn() && p == g_whyP && w == (g_whyC >> 6)) {
          const int c = g_whyC;
          std::fprintf(g_fill, "P f%lld ser%u pos%lld y%d d%d a%u b%u there%u ta%u tb%u vc%d vr%d blk%d blkRef%d lone%d dyn%d ver%d prov%d young%d\\n", g_frame, frameSerial_, pos, y, d, a[c], b[c], there[c], ta[c], tb[c],
                       WB(vc[w]), WB(vr[w]), WB(blk[w]), WB(blkRef[w]), WB(lone[size_t(brow) * words + size_t(w)]), WB(rowHasDyn ? dynWords[size_t(w)] : 0ull), WB(alreadyVer), WB(store_->prov[at + size_t(w)]), int(youngMask));
        }
        uint64_t need = ~(alreadyVer | blockedMask) & full[size_t(w)];""")
rep("""        mask[size_t(w)] = take;
        proved[size_t(w)] = moved;""",
"""        mask[size_t(w)] = take;
        proved[size_t(w)] = moved;
        if (whyOn() && p == g_whyP && w == (g_whyC >> 6)) std::fprintf(g_fill, "P   -> take%d moved%d\\n", WB(take), WB(moved));""")
# C: pending capture
rep("""      mask[size_t(w)] = m;
      open |= m != 0;
    }
    if (!open) continue;""",
"""      mask[size_t(w)] = m;
      open |= m != 0;
    }
    if (whyOn() && p == g_whyP) {
      const int w = g_whyC >> 6;
      std::fprintf(g_fill, "Q f%lld pos%lld y%d brow%d open%d tex%u cell%u blkW%d prov%d ver%d votes%d val%d\\n", g_frame, pos, y, brow, WB(mask[size_t(w)]), tRow[g_whyC], cur.cellRow(y)[g_whyC],
                   WB(blocked[size_t(brow) * words + size_t(w)]), WB(store_->prov[at + size_t(w)]), WB(store_->ver[at + size_t(w)]), store_->plainVotes[size_t(p - store_->origin) * C + size_t(g_whyC)] & 0x7F, store_->plainVal[size_t(p - store_->origin) * C + size_t(g_whyC)]);
    }
    if (!open) continue;""")
# D: flushPending
rep("""        any |= mask[size_t(w)] != 0;
      }
      if (any) {
        const uint16_t* bands = &pend.bands[slot * size_t(B) * 2];""",
"""        any |= mask[size_t(w)] != 0;
      }
      if (whyOn() && p == g_whyP) {
        const int w = g_whyC >> 6;
        std::fprintf(g_fill, "F f%lld pendpos%lld y%d brow%d open%d plain%d page%d near%d blk%d prov%d ver%d votes%d write%d finishing%d cell%u\\n", g_frame, pend.pos, y, brow, WB(open[w]), WB(plain[w]), WB(page[w]), WB(beside[w]), WB(blk[w]),
                     WB(store_->prov[at + size_t(w)]), WB(store_->ver[at + size_t(w)]), counted[g_whyC] & 0x7F, WB(mask[size_t(w)]), int(finishing), pend.cells[slot * size_t(C) + size_t(g_whyC)]);
      }
      if (any) {
        const uint16_t* bands = &pend.bands[slot * size_t(B) * 2];""")
open(p, 'w').write(s)
print('whytrace patched')
# dynamic marking of the target row
s = open(p).read()
def rep2(old, new):
    global s
    assert s.count(old) == 1, (old, s.count(old))
    s = s.replace(old, new)
rep2("""  bool markDyn(long long r, int k) {
    if (!has(r)) return false;""", """  bool markDyn(long long r, int k) {
    if (!has(r)) return false;
    if (whyOn() && r == g_whyP) std::fprintf(g_fill, "D f%lld row%lld band%d already%d\\n", g_frame, r, k, int(dyn[size_t(r - origin) * bands + size_t(k)]));""")
rep2("""    uint8_t& hits = store_->dynHitsRow(p)[k];
    hits = uint8_t(std::min(255, int(hits) + step));""", """    uint8_t& hits = store_->dynHitsRow(p)[k];
    hits = uint8_t(std::min(255, int(hits) + step));
    if (whyOn() && p == g_whyP) std::fprintf(g_fill, "H f%lld curPos%lld otherPos%lld dp%d y%d band%d hits%d step%d verify%d cur%u other%u store%u\\n", g_frame, curPos, otherPos, dp, y, k, int(hits), step, int(verifyAgreement), cur.bandRow(y)[k], other.bandRow(y + dp)[k], store_->bandRow(p)[k]);""")
open(p, 'w').write(s)
print('dyn trace patched')
# call sites of observeOnce, and band texture in the hit
s = open(p).read()
import re
calls = ["observeOnce(cur, *prevSig(), lastPos_, lastPos_, nullptr, -1, !still || redrawn)",
         "observeOnce(cur, *other, upos, otherPos, &cands, unexplainedPick, true)",
         "observeOnce(cur, *prevSig(), upos, prevPos_, &prevCands, pIdx, true)",
         "observeOnce(cur, *other, pos, otherPos, &cands, pick, true)",
         "observeOnce(cur, *prevSig(), lastPos_, lastPos_, nullptr, -1, true)",
         "observeOnce(cur, *prevSig(), fpos, prevPos_, &found, fp, true)",
         "observeOnce(*last_, *work_, pos, prevLastPos, &cands, pick, false)"]
for i, c in enumerate(calls):
    assert s.count(c) == 1, c
    s = s.replace(c, "(g_site = %d, %s)" % (i + 1, c))
s = s.replace("static long long g_frame = -1;\n", "static long long g_frame = -1;\nstatic int g_site = 0;\n", 1)
old = 'std::fprintf(g_fill, "H f%lld curPos'
assert s.count(old) == 1
s = s.replace(old, 'std::fprintf(g_fill, "H site%d texCur%u texOther%u ", g_site, cur.bandTexRow(y)[k], other.bandTexRow(y + dp)[k]), std::fprintf(g_fill, "f%lld curPos')
open(p, 'w').write(s)
print('site trace patched')
# bars(): every rectangle held back, with the pass
s = open(p).read()
old = """        if ((c1 - c0 + 1) * 3 < C || (r1 - r0 + 1) * 3 > blockRowCount_) continue;
        for (int r = r0; r <= r1; ++r)"""
assert s.count(old) == 1
s = s.replace(old, """        if ((c1 - c0 + 1) * 3 < C || (r1 - r0 + 1) * 3 > blockRowCount_) continue;
        if (whyOn()) std::fprintf(g_fill, "B f%lld pass%s rows %d-%d cols %d-%d\\n", g_frame, in == &closed_ ? "closed" : "joined", r0, r1, c0, c1);
        for (int r = r0; r <= r1; ++r)""")
open(p, 'w').write(s)
print('bars trace patched')
# snapshotDynamic rows written for the target row
s = open(p).read()
old = "        const uint8_t* row = chosenCopy ? &chosenCopy->px[size_t(y) * size_t(width_) * 4] : frame.row(y);\n        int spanStart = -1;"
if s.count(old) == 1:
    s = s.replace(old, old.split('\n')[0] + """
        if (whyOn() && p == g_whyP) {
          std::fprintf(g_fill, "S f%lld pos%lld srcPos%lld y%d brow%d copy%s replace%d p0 %lld p1 %lld k %d-%d bar%d blk%d\\n", g_frame, pos, srcPos, y, brow,
                       chosenCopy == &topCopy_ ? "top" : chosenCopy == &bottomCopy_ ? "bottom" : "none", int(replace), p0, p1, minK, maxK,
                       barRows_.empty() ? -1 : int(barRows_[size_t(brow)]), int((blk[g_whyC >> 6] >> (g_whyC & 63)) & 1));
          for (int r = 0; r < std::min(12, blockRowCount_); ++r) std::fprintf(g_fill, "%d", barRows_.empty() ? 9 : int(barRows_[size_t(r)]));
          std::fprintf(g_fill, "\\n");
        }
        int spanStart = -1;""")
    open(p, 'w').write(s)
    print('snapshot trace patched')
