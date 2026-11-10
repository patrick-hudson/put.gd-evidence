// Auto-scroll control loop for the rolling screenshot, behind platform interfaces.
#pragma once

#include <atomic>
#include <functional>
#include <cstdint>
#include <optional>
#include <string>

#include "scroll_stitcher.h"

namespace rollcap {

struct IScrollInjector {
  // Positive = scroll content down (wheel towards the user), negative = up.
  // Returns false when the event could not be delivered at all.
  virtual bool scrollNotches(int notches) = 0;
  virtual ~IScrollInjector() = default;
};

struct TimedFrame {
  FrameView view;           // valid until the next call to nextFrame() that returns a frame
  int64_t timestampMs = 0;  // monotonic, same clock as IClock
};

struct IFrameSource {
  // Waits up to timeoutMs for a frame newer than the last one returned.
  // Damage-driven streams may deliver nothing while the screen is static: that
  // is fine, the last returned view must then stay valid.
  virtual std::optional<TimedFrame> nextFrame(int timeoutMs) = 0;
  virtual ~IFrameSource() = default;
};

struct IClock {
  virtual int64_t nowMs() = 0;
  virtual void sleepMs(int ms) = 0;
  virtual ~IClock() = default;
};

struct SessionOptions {
  StitchOptions stitch;
  int settleMs = 120;               // no change in the moving band for this long = settled
  int settleMaxChangedRows = 2;     // same-y changed rows (loose rule) tolerated as "no change"
  int stepTimeoutMs = 1500;         // hard limit per settle wait
  int firstFrameTimeoutMs = 2000;
  double targetStepFraction = 0.60; // of the moving band
  double maxStepFraction = 0.75;
  int maxNotchesPerStep = 64;
  int endConfirmDelayMs = 400;      // wait before the confirming injection at a suspected end
  int totalTimeLimitMs = 180000;
  bool allowScrollBack = true;      // recover a jump past the overlap by scrolling back up
  double shortStepFraction = 0.7;   // offset < this * hint: final/partial step, keep px-per-notch
  // Optional log hook: every stitch attempt with the hint and notches used.
  std::function<void(const StepResult&, int hint, int notches)> onStep;
};

enum class SessionResult {
  EndOfContent,
  LimitReached,
  Cancelled,
  TimeLimit,
  InjectorFailed,
  LostTrack,   // a step could not be matched and could not be recovered (no gap is produced)
  Ambiguous,   // offset could not be decided (periodic/blank content without usable hint)
  NoFrames,
};
const char* toString(SessionResult);

struct SessionStats {
  int steps = 0;               // injections that were followed by a stitch attempt
  int notchesInjected = 0;     // absolute notches, including scroll-back
  double pxPerNotch = 0;       // last measured
  double minPxPerNotch = 0, maxPxPerNotch = 0;
  int retries = 0;             // re-settle retries after NoMatch/Ambiguous
  int scrollBacks = 0;
  int halvings = 0;
  int endConfirmations = 0;    // suspected ends that were confirmed by another injection
  int falseEnds = 0;           // suspected ends that moved on the confirming injection
  int reversed = 0;
  int lowConfidenceSteps = 0;
  int settleTimeouts = 0;
  int framesSeen = 0;
  int64_t elapsedMs = 0;
  int outputRows = 0;
  std::string lastError;
};

class ScrollSession {
 public:
  ScrollSession(IScrollInjector& injector, IFrameSource& source, IClock& clock,
                SessionOptions opts = {}, RowSink sink = {});
  // Runs to completion. The stitcher is finished on every exit path, so the
  // partial image is always usable (it never contains a gap).
  SessionResult run(const std::atomic<bool>* cancel = nullptr);

  const SessionStats& stats() const { return stats_; }
  ScrollStitcher& stitcher() { return stitcher_; }

 private:
  enum class Wait { Settled, TimedOut, Cancelled, TimeLimit, NoFrame };
  Wait waitSettled(int timeoutMs);
  int planNotches() const;
  bool inject(int notches);
  SessionResult finishWith(SessionResult r);

  IScrollInjector& injector_;
  IFrameSource& source_;
  IClock& clock_;
  SessionOptions opts_;
  ScrollStitcher stitcher_;
  SessionStats stats_;
  const std::atomic<bool>* cancel_ = nullptr;
  int64_t startMs_ = 0;
  bool haveFrame_ = false;
  FrameView last_{};
  FrameSignatures lastSig_, tmpSig_;
  int notchCap_ = 0;
  int verifiedRun_ = 0;
};

}  // namespace rollcap
