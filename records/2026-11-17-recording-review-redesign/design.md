# Recording review redesign: agreed design (council, 2026-11-17, rev 4)

Pictures: `../mock/review4-open.png` (as it opens), `../mock/review4-edit.png`
(editing, with insets for a time selection, cover placement and Blur), `../mock/review4-compact.png`
(1100×700, panel folded, Edits overlay with a cut selected) and `../mock/review4-light.png`
(the timeline in the light theme at normal and 150 % text); source `../mock/review4.html`
(`#open`, `#edit`, `#compact`, `#light`). This text and those
pictures must say the same thing; where they disagree, fix one. Rounds: `../proposals/`,
`../round2/`–`../round5/`. Manifesto: `../manifesto/`.

## Window

- Opens at 1440×900 within the work area (the owner lifted the 1366×768 rule for this
  window). Below ~1180×720 the right panel folds; the toolbar's panel toggle (labelled
  **Edits**, focusable) opens it as an overlay and focus returns to the toggle on close.
- Rows: title (40) · tool row (52) · viewer (takes all remaining height) · transport
  (42) · timeline (142 at normal text; grows with the font) · footer (56). The right
  panel is 280 px wide and runs from the tool row to the footer; the viewer, transport
  and timeline span the width left of it. Folded, the Edits overlay is 300 px wide,
  anchored under the Edits button (checked style while open), scrolls, takes focus on its
  default button, and Esc closes it with focus back on the button. While it is open the
  picture fits the uncovered width, left-aligned, so nothing plays under it; Play across
  closes it first.
- **Title:** "Review recording" · "Not uploaded". Duration, resolution, frame rate and
  codec are not shown in the window (they stay in History details and `inspect`).
- **Tool row** (image editor's tools and keys): Select **V** · Cut **C** · Redact **X** ·
  Blur **B** · Undo · Redo … **Fit · n%** (Fit / 100%; pan by drag and arrows at 100%,
  source-resolution pixels for the visible region) · panel toggle. Selecting an existing
  cover activates Select. Cut is enabled only with a time selection.
- **Viewer:** the frame at the playhead (or the skim position while hovering). Banners
  take space from the well, along its top edge, never over content:
  - placing a cover: "Draw the redaction · 0:08.2 – 0:12.6" (or "· whole recording")
    with a **Cancel** button (Esc); Save and Upload are disabled until the box is placed
    or cancelled;
  - Blur armed or a blur selected: "Blur may be reversible. Use Redact for private
    information." (warningSurface / warning, the image editor's wording).
- **Transport:** Play as a split button (its menu holds speeds 0.5×–4×; 1× default) ·
  previous / next frame (a film-frame glyph with an arrow, distinct from skip-to-start;
  tooltips name the `,` `.` keys) · output time / output length (m:ss.s) followed by
  muted "clip time" … "Preview is silent" (muted, with a speaker glyph) · timeline zoom
  button (magnifier + current level, "Fit" / "2×" / "4×"; tooltip "Zoom the timeline";
  Ctrl+wheel zooms around the pointer). The toolbar's "Fit · n%" has the tooltip "Zoom
  the picture".
- **Timeline** (no label column): ruler in recording (source) time, captioned "recording
  time" at its right end (ruler labels under the caption or the skim flag are skipped); filmstrip
  of ≈72 px tiles; trim brackets (accent), outside dimmed; cuts hatched with a "Cut · n s"
  chip (scissors glyph only when the chip does not fit); the selected cover's span as a
  20 % accent tint with a 3 px accent base line (no outline); a time selection as an
  accent-outlined, dashed range (a time selection and an edit selection never coexist);
  the playhead (cap on the ruler; a two-tone stroke, Theme text over an opposing outline,
  that ends above the Covers lanes); while paused and hovering, a thin skim line with its
  own time flag on the ruler, painted "≈0:05.3" until the exact frame arrives (a frame step
  or boundary jump updates frame and time together). **Covers** track: two lanes of named
  bars (idle bars in the neutral token, the selected cover in accent with handles), lane
  height from QFontMetrics (13 px at normal text), names elided, "+n" past two
  lanes; the selected bar's ends are drag handles that retime it; empty, it reads "No
  covers yet". All timeline colours come from Theme tokens (`review4-light.png`).
- **Right panel:**
  - Nothing edited yet: "No edits yet" · "Upload sends the whole clip." · five
    gestures (brackets trim; a pointer glyph: drag selects time; C / Del cut; X / B
    redact or blur; Ctrl+Z undoes). No keyboard-help disclosure, no clip facts.
  - A cover selected: name · "Covered pixels are removed from the saved and uploaded
    clip." (Blur: the warning sentence instead) · **Shows from →** and **Until →** (link
    buttons that seek to the first / last *kept* covered frame; Home / End do the same;
    disabled with "Excluded from output" when no covered frame is kept; one frame step
    from there shows the uncovered frame just outside) with
    m:ss.s fields (frame number in the tooltip) and **Set to playhead** buttons (keys
    ⇧I / ⇧O in their tooltips; accessible names name the edge) · Redact | Blur
    (blur adds its strength).
  - A cut selected: span and "n s left out of the clip" · **Restore** (default button)
    · **Play across** (from 1 s of kept footage before the seam).
  - A time selection: span and length · Cut · Redact · Blur.
  - Below (once anything is edited): **Edits**, every trim, cut and cover in source
    order with icon, name and span (no count); a selected row shows its verb (Trim: Reset,
    cover: Remove) in place of the span only when the panel above does not already offer
    it (a selected cut keeps its span: Restore is above); other rows show their verb on
    hover.
- **Footer:** Format ▾ ("MP4 · with system audio"; codec and limits inside the menu,
  GIF/WebP state "no sound" here) … **Discard…** (keeps today's confirmation) · 12 px ·
  **Save a copy…** · destination ▾ ("Project archive · Shared link", or "· Private
  upload": says what Upload produces) · **Upload** (primary, closes at once).

## Interaction rules

- Opens paused on the first frame, Upload as the default button. Thumbnails: 12 tiles at
  Fit, up to 24 visible tiles per zoom batch, filled by one cancellable worker that opens
  the clip once, seeks backward to the keyframe before each tile time, decodes only that
  keyframe packet and scales straight to tile size; the two end tiles first; cached by
  keyframe time; placeholders (surface) until then; exact-time tiles only lazily when
  zoomed. Never a whole-clip decode pass. Scrubbing and Upload never wait for the worker.
  Measured on m74 (i5-6500T, 3-minute 4K60 clip, nightly's FFmpeg 9.0.2): ends in 156 ms,
  12 tiles in 433 ms, 24 in 739 ms (p95, warm; 490 ms / 846 ms cold), one core, 55 MiB;
  a full decode takes 24 s (`../test/results.md`).
- Drag on the filmstrip selects a half-open source-time span; `[` `]` set it from the
  keyboard; a click seeks and clears; **Esc** clears.
- Paused hover skims the viewer: the tile at once; after ~120 ms at rest one exact-frame
  request (at most one in flight, cancelled when the pointer moves; the input stays open)
  replaces the tile when it arrives, and the flag drops its "≈" then. On m74 that frame
  takes 217 ms median, 328 ms p95 at 4K (130 / 199 ms at 1080p). Leaving the strip
  restores the playhead frame; skim never moves the playhead.
- **C**, **Delete** or **Backspace** on a time selection cuts it (Delete/Backspace act in
  the viewer, timeline and Edits list only, never in a focused field). A cut stays in
  place, hatched; playback jumps it; output length drops. After *making* a cut the
  playhead lands 1 s before the seam in output time, clamped to the first kept frame
  (unless an agent action set the playhead).
- Clicking a cut selects it: its edges get handles (drag to adjust), the panel offers
  Restore and Play across. Selecting a cut from Edits seeks to the first kept frame after
  it (last kept frame before a trailing cut). Delete never restores; Restore or Ctrl+Z.
- **X** / **B** arm a cover for the time selection (snapped outward to whole frames), or
  for the whole source `0..duration` with nothing selected; the placement banner names
  which. On arming, the viewer pauses on the playhead frame if it is inside the
  selection's kept footage, else on the first kept frame in it, else (all excluded) on
  its first source frame with "Excluded from output". Drag a box to place it; one command
  creates rect + span. Delete removes a selected cover.
- Selecting a cover seeks to its first visible frame; one wholly outside kept footage
  shows its start paused with "Excluded from output".
- Alt+←/→ steps through edits in any layout. `,` `.` step a frame; arrows 0.1 s, Shift
  1 s; Space plays; I/O set trim; Shift+I/O retime the selected cover; Home/End go to the
  selected cover's first/last frame (else the kept ends).
- Undo/redo in the resident: one step per committed gesture, a nudge run is one step,
  each undo/redo is a new revision, history covers trim/cuts/covers only. Ctrl+Z while
  placing cancels the placement.
- Ctrl+Enter finishes a pending drag or nudge and uploads the acknowledged revision; it
  does nothing while placing a box or with a menu open.

## Model and agent control

- `RecordingEdit.cuts [{id,start,end}]` in source time; `addCut` (merges, clamps,
  refuses an empty result), `updateCut`, `removeCut`; `undo`, `redo`. Covers stay in
  source time; export clamps them to kept spans.
- Exporter (FFmpeg) joins kept spans for video and audio on the frame grid; GIF/WebP
  limits count kept time; playback, export, limits and progress share one kept-span map.
- `recording.review` gains: select range / clear, cut, select cut, adjust cut, restore
  cut, play across, undo, redo, arm redact/blur, place, cancel placement, select edit /
  next / previous, seek cover start/end, timeline zoom / fit, viewer zoom / pan, frame
  step, panel toggle. Inspect adds selection, cuts, edits list, zoom, panel state,
  placement banner, output duration, source and output playhead. Every control routes
  through the same handler as its UI.

## Not in this design

Waveform, crop, text, speed-up segments, zoom/pan effects, click emphasis, automatic
mask timing, J/K/L shuttle.

## References (round 5)

Trim brackets with the edge frame: QuickTime, Photos. Skimmer with its own line: Final
Cut Pro. Select range then cut: Snagit, Tella, Loom (Delete cuts). Cut kept visible and
recoverable in place: Screen Studio's scissors marker, Clipchamp. Timed opaque cover
with timeline edges: Camtasia. Check first and last covered frame: Tella's guidance.
Leave at once: CleanShot X. Say what Upload produces: Loom, ScreenPal. Sources in
`../round5/opus.md` and `../round5/sol.md`.

## Also found

The code opens the review at 820×720 (`ReviewWindow.cpp` `defaultSize()`) while the
contract says 960×600; this design replaces both.
