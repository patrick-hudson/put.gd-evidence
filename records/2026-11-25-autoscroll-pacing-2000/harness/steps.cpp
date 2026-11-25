#define main original_test_main
#include "tests/unit/test_scroll_session.cpp"
#undef main
// Per-step notches for Sol's #2000 case (3.5 s stall, damage-only, 40 px a notch).
int main() {
  const Document doc = page(96);
  for (int stall : {0, 3500}) {
    Harness h;
    FakeAppSpec as;
    as.pxPerNotch = 40;
    as.animMinMs = as.animMaxMs = 1;
    as.damageOnly = true;
    as.stallAfterFirstMoveMs = stall;
    SessionOptions so = options(true);
    std::vector<std::pair<int64_t,int>> steps;
    so.onStep = [&](int n, RunPoint) { steps.push_back({h.clock.nowMs() - h.t0, n}); };
    h.run(doc.img, as, so);
    std::printf("stall=%d %s, %lld ms\n", stall, counts(h).c_str(), (long long)h.stats.elapsedMs);
    for (auto [t, n] : steps) std::printf("%lld:%d ", (long long)t, n);
    std::printf("\n");
  }
}
