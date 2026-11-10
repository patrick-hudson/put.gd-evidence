#include "scroll_session.h"

#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <utility>

namespace rollcap {

const char* toString(SessionResult r) {
  switch (r) {
    case SessionResult::EndOfContent: return "EndOfContent";
    case SessionResult::LimitReached: return "LimitReached";
    case SessionResult::Cancelled: return "Cancelled";
    case SessionResult::TimeLimit: return "TimeLimit";
    case SessionResult::InjectorFailed: return "InjectorFailed";
    case SessionResult::LostTrack: return "LostTrack";
    case SessionResult::Ambiguous: return "Ambiguous";
    case SessionResult::NoFrames: return "NoFrames";
  }
  return "?";
}

ScrollSession::ScrollSession(IScrollInjector& injector, IFrameSource& source, IClock& clock,
                             SessionOptions opts, RowSink sink)
    : injector_(injector), source_(source), clock_(clock), opts_(opts),
      stitcher_(opts.stitch, std::move(sink)) {}

bool ScrollSession::inject(int notches) {
  stats_.notchesInjected += std::abs(notches);
  return injector_.scrollNotches(notches);
}

SessionResult ScrollSession::finishWith(SessionResult r) {
  stitcher_.finish();
  stats_.elapsedMs = clock_.nowMs() - startMs_;
  stats_.outputRows = stitcher_.outputHeight();
  return r;
}

// Settled = no frame changed versus its predecessor for settleMs. "Changed" is
// decided on row signatures of the moving band: more than settleMaxChangedRows
// rows fail the loose same-y rule (<= bands-minBandsEqual bands differ), or any
// margin row (scrollbar) changed. A caret, spinner or hover effect confined to
// two of eight bands therefore never keeps the frame "moving".
ScrollSession::Wait ScrollSession::waitSettled(int timeoutMs) {
  const int64_t start = clock_.nowMs();
  const int64_t deadline = start + timeoutMs;
  int64_t lastChange = start;  // at least settleMs after the injection
  for (;;) {
    if (cancel_ && cancel_->load()) return Wait::Cancelled;
    const int64_t now = clock_.nowMs();
    if (now - startMs_ >= opts_.totalTimeLimitMs) return Wait::TimeLimit;
    if (haveFrame_ && now - lastChange >= opts_.settleMs) return Wait::Settled;
    if (now >= deadline) {
      if (!haveFrame_) return Wait::NoFrame;
      ++stats_.settleTimeouts;
      return Wait::TimedOut;
    }
    const int64_t wakeAt = haveFrame_ ? std::min(lastChange + opts_.settleMs, deadline) : deadline;
    const int wait = int(std::max<int64_t>(1, wakeAt - now));
    std::optional<TimedFrame> f = source_.nextFrame(wait);
    if (!f) continue;
    ++stats_.framesSeen;
    tmpSig_.compute(f->view, opts_.stitch);
    bool changed = true;
    if (haveFrame_ && lastSig_.height == tmpSig_.height && lastSig_.width == tmpSig_.width) {
      int top = 0, bottom = tmpSig_.height;
      if (stitcher_.hasFrame()) {
        top = stitcher_.movingBandTop();
        bottom = stitcher_.movingBandBottom();
      }
      changed = framesDiffer(lastSig_, tmpSig_, top, bottom, opts_.stitch, opts_.settleMaxChangedRows);
    }
    if (changed) lastChange = std::max(lastChange, f->timestampMs);
    std::swap(lastSig_, tmpSig_);
    last_ = f->view;
    haveFrame_ = true;
  }
}

int ScrollSession::planNotches() const {
  const double px = stats_.pxPerNotch;
  if (px <= 0) return 1;
  const int band = stitcher_.movingBandBottom() - stitcher_.movingBandTop();
  double maxPx = opts_.maxStepFraction * band;
  double targetPx = opts_.targetStepFraction * band;
  // Keep informative rows of the reference in the overlap when it has any, so
  // that a blank/flat lower part does not force a hint-only (blind) step.
  const int evidence = stitcher_.maxEvidenceStep();
  if (evidence >= 0) {
    maxPx = std::min(maxPx, double(evidence));
    targetPx = std::min(targetPx, maxPx);
  } else if (stats_.minPxPerNotch > 0 && stats_.maxPxPerNotch > 1.03 * stats_.minPxPerNotch) {
    // Blind (hint-only) step and the app's px-per-notch varies: keep it to one
    // notch so the unverifiable error stays as small as possible.
    return 1;
  }
  int n = int(std::lround(targetPx / px));
  n = std::max(1, n);
  while (n > 1 && n * px > maxPx) --n;
  n = std::min({n, notchCap_, opts_.maxNotchesPerStep});
  return std::max(1, n);
}

SessionResult ScrollSession::run(const std::atomic<bool>* cancel) {
  cancel_ = cancel;
  startMs_ = clock_.nowMs();
  notchCap_ = opts_.maxNotchesPerStep;

  auto waitFail = [&](Wait w) -> std::optional<SessionResult> {
    if (w == Wait::Cancelled) return finishWith(SessionResult::Cancelled);
    if (w == Wait::TimeLimit) return finishWith(SessionResult::TimeLimit);
    if (w == Wait::NoFrame) return finishWith(SessionResult::NoFrames);
    return std::nullopt;
  };

  if (auto f = waitFail(waitSettled(opts_.firstFrameTimeoutMs))) return *f;
  stitcher_.addFrame(last_, lastSig_, kNoHint);

  int notches = 1;
  bool endPending = false;
  int oneNotchFailures = 0;

  for (;;) {
    if (cancel_ && cancel_->load()) return finishWith(SessionResult::Cancelled);
    if (clock_.nowMs() - startMs_ >= opts_.totalTimeLimitMs) return finishWith(SessionResult::TimeLimit);

    if (!inject(notches)) {
      stats_.lastError = "injector refused the scroll event";
      return finishWith(SessionResult::InjectorFailed);
    }
    ++stats_.steps;
    if (auto f = waitFail(waitSettled(opts_.stepTimeoutMs))) return *f;
    const int hint = stats_.pxPerNotch > 0 ? int(std::lround(stats_.pxPerNotch * notches)) : kNoHint;
    const int unc = hint < 0 ? 0 : int(std::ceil(notches * (stats_.maxPxPerNotch - stats_.minPxPerNotch)));
    StepResult r = stitcher_.addFrame(last_, lastSig_, hint, unc);
    if (opts_.onStep) opts_.onStep(r, hint, notches);

    if (r.status == StepStatus::NoMatch || r.status == StepStatus::Ambiguous) {
      // 1) Transient: the frame may not have been final (late repaint, overlay).
      ++stats_.retries;
      if (auto f = waitFail(waitSettled(opts_.stepTimeoutMs))) return *f;
      r = stitcher_.addFrame(last_, lastSig_, hint, unc);
      if (opts_.onStep) opts_.onStep(r, hint, notches);
    }
    if (r.status == StepStatus::NoMatch || r.status == StepStatus::Ambiguous) {
      const bool ambiguous = r.status == StepStatus::Ambiguous;
      if (ambiguous && hint < 0) {
        stats_.lastError = "first step is ambiguous (periodic or blank content) and no px-per-notch is known";
        return finishWith(SessionResult::Ambiguous);
      }
      if (!opts_.allowScrollBack) {
        stats_.lastError = "step could not be matched; scrolling further down cannot reconnect to the "
                           "last stitched frame without scrolling back";
        return finishWith(SessionResult::LostTrack);
      }
      // 2) Scroll back by the same amount, re-find the reference, halve the step.
      if (!inject(-notches)) {
        stats_.lastError = "injector refused the scroll-back event";
        return finishWith(SessionResult::InjectorFailed);
      }
      ++stats_.scrollBacks;
      if (auto f = waitFail(waitSettled(opts_.stepTimeoutMs))) return *f;
      const StepResult back = stitcher_.addFrame(last_, lastSig_, 0);
      if (opts_.onStep) opts_.onStep(back, 0, -notches);
      if (back.status != StepStatus::NoMovement && back.status != StepStatus::Appended &&
          back.status != StepStatus::Reversed) {
        stats_.lastError = std::string("after scrolling back the last stitched frame was not found (") +
                           toString(back.status) + ")";
        return finishWith(back.status == StepStatus::LimitReached ? SessionResult::LimitReached
                                                                  : SessionResult::LostTrack);
      }
      if (back.status == StepStatus::Reversed) ++stats_.reversed;
      if (notches == 1 && ++oneNotchFailures >= 2) {
        stats_.lastError = "a single notch scrolls further than the overlap allows; enlarge the region";
        return finishWith(SessionResult::LostTrack);
      }
      notchCap_ = std::max(1, notches / 2);
      verifiedRun_ = 0;
      ++stats_.halvings;
      notches = planNotches();
      continue;
    }

    switch (r.status) {
      case StepStatus::Appended: {
        if (endPending) ++stats_.falseEnds;
        endPending = false;
        oneNotchFailures = 0;
        if (r.lowConfidence) ++stats_.lowConfidenceSteps;
        // Learn px-per-notch from verified steps; a low-confidence step only
        // teaches it when nothing is known yet (and it had pixel evidence).
        const bool learn = r.lowConfidence ? (hint < 0 && r.evidenceRows > 0) : true;
        if (learn && r.offset > 0 && (hint < 0 || r.offset >= opts_.shortStepFraction * hint)) {
          const double px = double(r.offset) / notches;
          stats_.pxPerNotch = px;
          stats_.minPxPerNotch = stats_.minPxPerNotch > 0 ? std::min(stats_.minPxPerNotch, px) : px;
          stats_.maxPxPerNotch = std::max(stats_.maxPxPerNotch, px);
        }
        // A halved cap recovers after a run of verified steps.
        if (!r.lowConfidence && ++verifiedRun_ >= 3 && notchCap_ < opts_.maxNotchesPerStep) {
          notchCap_ = std::min(opts_.maxNotchesPerStep, notchCap_ * 2);
          verifiedRun_ = 0;
        }
        if (r.lowConfidence) verifiedRun_ = 0;
        notches = planNotches();
        break;
      }
      case StepStatus::LimitReached:
        return finishWith(SessionResult::LimitReached);
      case StepStatus::NoMovement:
        if (endPending) {
          ++stats_.endConfirmations;
          return finishWith(SessionResult::EndOfContent);
        }
        // Possibly the end, a dropped event or a slow lazy load: confirm once.
        endPending = true;
        clock_.sleepMs(opts_.endConfirmDelayMs);
        break;
      case StepStatus::Reversed:
        ++stats_.reversed;
        break;
      default:
        stats_.lastError = std::string("stitcher returned ") + toString(r.status);
        return finishWith(SessionResult::LostTrack);
    }
  }
}

}  // namespace rollcap
