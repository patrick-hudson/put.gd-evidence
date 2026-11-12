// Replays real frames (raw BGRX files) through the stitcher: replay7 W H POS:FILE [POS:FILE ...]
// The hint of each frame is its true distance from the last accepted one, as a loop that knows its wheel gives it.
#include "core/ScrollStitcher.h"
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <string>
#include <vector>
using namespace putgd::scroll;
int main(int argc, char** argv) {
  const int W = std::atoi(argv[1]), H = std::atoi(argv[2]);
  StitchOptions o;
  o.lateBarIsFooter = true;  // as the helper sets it
  ScrollStitcher st(o);
  int refPos = 0;
  for (int i = 3; i < argc; ++i) {
    const std::string a = argv[i];
    const int pos = std::atoi(a.substr(0, a.find(':')).c_str());
    std::ifstream in(a.substr(a.find(':') + 1), std::ios::binary);
    std::vector<uint8_t> px(size_t(W) * H * 4);
    in.read(reinterpret_cast<char*>(px.data()), std::streamsize(px.size()));
    const FrameView f{px.data(), W, H, std::ptrdiff_t(W) * 4};
    const StepResult r = st.addFrame(f, i == 3 ? kNoHint : pos - refPos);
    std::printf("pos %6d true %5d: %-13s offset %5d score %.2f evidence %4d appended %4d fixed %d/%d%s height %d\n", pos, pos - refPos, toString(r.status), r.offset, r.score, r.evidenceRows, r.appendedRows, r.fixedTop,
                r.fixedBottom, r.ownPace ? " own-pace" : "", st.outputHeight());
    if (r.status == StepStatus::First || r.status == StepStatus::Appended || r.status == StepStatus::Reversed || r.status == StepStatus::NoMovement) refPos = pos;
  }
  return 0;
}
