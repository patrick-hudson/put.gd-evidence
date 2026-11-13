Copy text and read QR codes from a capture: a new **Copy text** action, text tools in the editor, and QR codes for links, on every declared desktop.

This issue is the whole plan for one build. Patrick approved the feature on 2026-11-12, which lifts the "no OCR" non-goal in `AGENTS.md`, `docs/design/overview.md` and `docs/design/README.md`. A first documentation pull request records only that; the feature's own documentation follows the code.

## Why

Spectacle (Plasma 6.6), the Windows Snipping Tool, ShareX 22, CleanShot X and Shottr copy text out of a screenshot, and most read QR codes in the same pass. put.gd has neither. The Snipping Tool also redacts emails and phone numbers in one click.

## Baseline experiment

Taken on d69 (Debian 13) with the `tesseract` 5.5.0 and `ZXingReader` 2.3.0 command-line tools over twelve real put.gd and desktop captures, light and dark. These are experiments that shaped the plan. They are not acceptance of any put.gd build. The inputs, script and results are in `~/work/ocr-spike-1112` on d69.

| Measure | Result |
| --- | --- |
| Tesseract, whole process, crops up to 1000 × 240 | 0.12 to 0.49 s, 34 to 40 MiB peak RSS |
| Tesseract, 1180 × 820 window: 1× (1 MP), 2× (3.9 MP), 3× (8.7 MP) | 0.42 s and 42 MiB; 0.65 s and 48 MiB; 0.94 s and 70 MiB |
| Dark UI text at 1× | wrong: `synthetic-2.txt` read as `syntheticatet`, and a row of controls was missed |
| The same at 2× with the page inverted | read correctly; light paragraphs and menus were already correct at 1× |
| Icons beside text | read as stray `&`, `W`, `®` |
| ZXing QR decode inside a 1180 × 820 capture | 0.01 to 0.03 s, 7 to 11 MiB; a 74 px code decoded |
| Debian's `libtesseract.so.5` | links libcurl and libarchive and, through them, about fifty libraries |
| Debian's `libZXing.so.3` | 1.35 MB, links only libc and libstdc++ |

## Behaviour

### 1. Copy text (action `text`)

1. **Trigger:** tray entry "Copy text from region", a button on the main window's command band, its own hotkey (unassigned by default), or `action.invoke {"action":"text"}`. Capture delay applies as it does to a region capture. The screen-lock refusal applies as it does to every capture.
2. **Select:** the same region selector as Capture region on each desktop, live or screenshot-first as configured. Escape cancels.
3. **Recognize:** the pixels go to a temporary helper. Codes are decoded first and their area is filled with the background, then the text is recognized.
4. **Result:** one plain-text clipboard write, then a notification:

   | Found | Clipboard | Notification |
   | --- | --- | --- |
   | Text | the text | "Copied 214 characters" |
   | Text and codes | the text with each code's content on a line of its own | "Copied 214 characters and 1 code" |
   | Only codes | the content, one per line | "Copied 1 code" |
   | Nothing | unchanged | "No text found" |
   | A newer clipboard change by the user | unchanged | "Text not copied: the clipboard changed" |

   When the result was cut at a size limit, the notification adds "The text was cut at the size limit", and the editor's panel says the same.

   A code's line goes before the first text line whose top edge is below the code's centre. The notification never contains recognized text, a host name or code content, and has no action buttons. With notifications off the copy still happens.
5. **Nothing recognized is stored.** No upload, no artifact and no local copy. A text capture that succeeds or is cancelled leaves no History item; while it runs it shows as current work like any accepted operation, and a failure is listed like Capture failed. Recognized text and code content are never written to the journal, the History database, logs, UI checkpoints or diagnostics.
6. put.gd never opens a link from this action.

### 2. Editor

- **Copy text tool (G):** a new tool at the end of the toolbar, after Blur, behind its own separator. Choosing it starts recognition for the current revision; nothing is recognized before that. While it is the active tool, a new recognition revision starts recognition again by itself; with any other tool active it does not.
  - Selection works like text in a document. Press on a word and drag to another: every word between them in reading order is selected and tinted on the canvas. Shift+click extends, double-click takes the line, Ctrl+A takes everything.
  - Ctrl+C copies the selection while the canvas has focus. In a text field Ctrl+C stays the field's own.
  - Escape clears the selection; Escape again returns to Select.
  - The tool's panel shows the state ("Recognizing…", "214 words", "No text found"), **Copy selection**, **Copy all text** (codes included, as in the action), and the note "Reads the original image. Marks you added are not included, and Blur does not hide text from it."
- **Quick redact:** a menu in the Redact tool's panel, with "Suggestions only. Recognition can miss text." always beside it. Each category adds ordinary Redact marks, as one undo step, and the result line says "Added 3 suggested redactions" or "No matches found. Text can still be there." There is no "safe" verdict and no upload confirmation. Choosing a category with no result for the current revision starts recognition and waits for it, or joins the job already running for that revision, under that job's deadline. If a Redact mark or the crop changes while it waits, it ends with `edit_stale` and adds nothing. `editor.apply` with `redactText` behaves the same.
- **Codes:** the Copy text panel lists each code found, one row each: its kind, its content on one elided line, Copy, and Open link for a valid http or https URL. A URL's row shows the whole URL, wrapped, with the host in its ASCII form, so it is in view before Open link is pressed; Open link then opens it at once, with no dialog. A binary code's row shows its kind and length only, with Copy and Open link disabled.
- **What recognition reads:** the source pixels inside the current crop, with every Redact mark already applied as opaque black. Other marks (arrows, text, blur, highlight) are not part of the input.
- **Staleness:** results belong to a recognition revision, which changes only when a Redact mark changes (add, move, resize, remove) or the crop does, including by undo or redo. Arrows, text and other marks do not change it. A new recognition revision cancels a job that is running and discards the results, clears any text selection and the code list, and rejects a result that arrives late. A word or code under a Redact mark can never be copied or returned: besides blacking the pixels before recognition, any word box or code quadrilateral that touches a Redact mark is dropped from the result, so a code that still decodes through its error correction is not reported.

### 3. History

- **Copy text** on an image item, read from its retained local copy (the same rule as Edit again). With no local copy it is disabled and says why. put.gd never downloads an upload to read it.
- **Show QR code** on an item whose link Copy link would copy. It opens a small window with the code, Copy image and Save. A link that has expired but can be refreshed is refreshed first, as Refresh and copy link does. It is disabled, with the reason, for a private, removed or revoked link and for an expired one that cannot be refreshed.
- History search stays name-only. put.gd recognizes text only when asked, never in the background.

## Decisions

### 1. Engines

- **Text:** Tesseract 5 through its C++ API, LSTM engine only. It is Apache-2.0 and packaged on every supported distribution.
- **Reading codes:** ZXing-cpp (Apache-2.0), formats QR Code, Micro QR Code, Data Matrix and Aztec. Linear barcodes and PDF417 are not read.
- **Writing QR codes:** a vendored copy of Nayuki's QR Code generator (MIT, `qrcodegen.cpp` and `qrcodegen.hpp`), not ZXing. The distributions ship ZXing 2.2.1, 2.3.0 and 3.1.1, whose writer APIs differ (3.x writes through zint). Vendoring removes that variance, and QR writing then needs no helper: it takes a link put.gd already holds and maps no library. It is compiled into the core library, so the resident (`history.qr` copy and save) and `putgd-ui` (the window) share it; the resident's code-size change is recorded in the A/B.
  - It is pinned at v1.8.0, the latest release (checked 2026-11-12; upstream's master carries unreleased changes). Its tag commit and both files' SHA-256 go in the dependency lock, and `tools/verify_dependencies.py` checks them.
  - `tools/releases/sbom.py` adds it as a component of every package.
  - Its MIT notice is installed with every package through `packaging/linux/runtime-notices.txt.in` and the AppImage notices, and listed in `THIRD_PARTY_NOTICES.md`.
- Neural engines (PaddleOCR and similar through ONNX Runtime) were not chosen: a runtime of 100 MB or more with no package on most targets.

### 2. A new temporary helper, `putgd-ocr`

It keeps the image worker's control protocol (`docs/design/image-worker.md`: framed control pipe, nonce, build identity, authenticated checkpoint, parent deadline) and differs in how data moves and how the process is confined.

| Aspect | `putgd-ocr` |
| --- | --- |
| Task | `recognize`: text and codes from one image. The request says whether word boxes are wanted (`words`) and whether unfiltered candidates are (`candidates`, the editor only) |
| Input | a sealed memfd (`F_SEAL_WRITE`, `SHRINK`, `GROW`; precedent in `src/platform/wayland/RegionProtocol.cpp`) holding width, height, stride and **8-bit grey** pixels. The parent decodes, applies Redact marks, flattens alpha and converts to grey. The parent fills it with `write()` and closes its copy once the child has started, so the mapping never counts in the parent. Because it is sealed, the helper fills code areas in its per-band copies. The helper stages nothing in a directory: recognized text never reaches a disk, and neither do pixels from the screen, the clipboard image or a PNG file. A JPEG from the `file`, `clipboard` or `history` source is decoded by the existing image worker, which stages a copy of that file under `/tmp` as it does for every import today |
| Output | a second memfd the parent opened, at most 8 MiB of JSON, written only through that inherited descriptor (never reopened by path) and accepted only after the authenticated checkpoint and a zero exit |
| Result bounds | text at most 1 MiB; 20,000 words of at most 256 bytes each; 64 codes of at most 8 KiB each. Over a bound the result is cut there and `truncated` is true. The 8 MiB output cap governs all of them together: candidates are cut first, then words, then codes, then text |
| Errors from the child | `input_excessive`, `text_job_io`, `language_unavailable`, `engine_unavailable`, `helper_sandbox_unavailable`, each with a fixed message and no paths or payload |
| Errors from the parent | `text_job_timeout` (deadline), `text_job_failed` (crash, signal, a resource limit, nonzero exit), `text_incompatible` (build or protocol mismatch, malformed frame), `text_busy`, `text_helper_missing` |
| Handshake | role `text-job`, nonce, generation, and the compiled build manifest |
| Deadline | fixed by the parent before it prepares the input, 20 s at most; exact-child terminate then kill; cancellation checked between waits |
| Process | QtCore only: it links a new QtCore-only text-job protocol library (modelled on `putgd_session_protocol`), not `putgd_core`, which brings QtGui and QtSql. The audits also refuse `putgd-ocr` if it needs QtGui, QtSql, QtNetwork or QtDBus. Pixels go to Tesseract with `SetImage(data, width, height, 1, stride)` and to ZXing as an `ImageView`; no image file reader in Qt or Leptonica is ever used. No display, session socket, configuration or credentials |
| Environment | cleared, then only the data path, `OMP_THREAD_LIMIT=1` and a C UTF-8 locale. Descriptor 2 stays a capped, discarded stderr pipe, as for the image worker. The two memfds arrive at fixed descriptor numbers, set by `dup2` in the child-process modifier (the `PosterJob` and `RegionProcess` way; Qt 6.4.2 has no other). Every other inherited descriptor is closed first |
| Lifetime | one job, then exit, with `PR_SET_PDEATHSIG` so it dies with its parent. One job at a time per parent: an independent second request while one runs is refused at once with `text_busy` (a second Copy text press gets the notification "Text recognition is still running"); nothing queues. The editor's own restart on a new recognition revision first waits for the cancelled child to be reaped. The parent starts and waits for the helper on one thread that outlives it, because `PR_SET_PDEATHSIG` follows the starting thread; the `getppid()` check from `src/ui/ChildProcess.h` moves to where core can use it |

**Confinement**, installed at the top of `main`, before any input is read. Any part that cannot be installed fails the job with `helper_sandbox_unavailable`; that failure is the authority. Capabilities report the known prerequisite in advance (the kernel's Landlock version) and nothing stronger.

- `PR_SET_NO_NEW_PRIVS` and `PR_SET_DUMPABLE 0`.
- Resource limits: no core file; `RLIMIT_DATA` (private writable memory, not the address space) at about one and a half times the job's memory budget; CPU time just above the deadline; file size 8 MiB, which is also the output cap; a small descriptor count. No tight `RLIMIT_AS`: mapped libraries and glibc's reservations would trip it.
- A sanitizer build, marked at compile time as `PUTGD_POSTER_SANITIZED` is for `PosterJob`, skips the memory limit, the dumpable setting and the `ptrace` kill, which the sanitizers need. Confinement tests run on unsanitized builds only.
- **Landlock** (system calls only, no library), ABI 3 or later so that truncation by path is covered; every target's kernel gives ABI 4 or later. Where ABI 6 exists the signal and abstract-socket scopes are used as well, so the helper cannot signal the user's other processes. Read-only access to the system library and data directories, the AppImage mount, the language data directories and `/proc/self`, plus the CPU entries OpenMP reads. No write access anywhere; output leaves only through the memfd. This is what stops a compromised helper from writing `~/.bashrc` or reading `~/.aws/credentials`.
- **seccomp** deny-list on all threads (`SECCOMP_FILTER_FLAG_TSYNC`), hand-written BPF for x86_64, the only packaged architecture, with the architecture checked and x32 numbers rejected. `socket` and `connect` fail with `EPERM`. These kill the whole process (`SECCOMP_RET_KILL_PROCESS`): `execve`, `execveat`, `ptrace`, `process_vm_readv`, `process_vm_writev`, `pidfd_getfd`, the three `io_uring` calls, `bpf`, `perf_event_open`, `userfaultfd`, `keyctl`, `unshare`, `setns`, `mount`, `pivot_root`, `chroot`, `fork`, `vfork`, and any `clone` that is not a plain thread creation (a new process or a new namespace). `clone3` returns `ENOSYS`, so glibc falls back to `clone`. The helper can therefore start threads but no process, and nothing can outlive it. Everything else stays allowed, so later allocation, file reads and thread creation by Tesseract or OpenMP are unaffected.
- The capabilities prerequisite comes from the resident's own Landlock version query; no helper is started for it.
- CI's tests and package builds run in containers, so first light includes proving both mechanisms work there. Package acceptance probes the Landlock ABI on every target, and the AppImage's relocation test starts the helper with an empty environment, so its library path must come from its own RUNPATH. There is no precedent for either mechanism in `src`.

The resident, `putgd-ui`, `putgd-record` and the workers never link or load Tesseract, Leptonica or ZXing. The package audits enforce it: `tools/releases/audit_native.py` and the AppImage audit already walk every ELF, and gain the rule that only `putgd-ocr` may need those libraries. The editor (`putgd-ui --edit-image`) starts the helper as its own child through the same core class the resident uses. The helper is added to `cmake/ProductBinaries.cmake`, the native audit's `PROGRAMS`, `tools/ci/check_layers.py` and the AppImage component list.

### 3. Memory and time bounds for recognition

The configurable image limits do not bound this job, so it has its own.

- **Admission:** input above 24 megapixels is refused (`input_excessive`), the editor's own limit. As 8-bit grey that is at most 24 MiB, shared with the parent through the memfd.
- **Codes first:** ZXing reads the full grey image, then each decoded code's area is filled with the background. Bands therefore never need a code.
- **Scale:** chosen from the estimated text height (decision 4), and limited by a cap on the total scaled pixels of one job. The cap is 8 megapixels, measured on m74 (the 32 first planned sent 24-megapixel inputs into the CPU limit). Above the cap the scale falls toward 1×. Scaling is done one band at a time from the unscaled input; the whole scaled image never exists.
- **Single pass:** when the scaled image is at most 8 megapixels it is recognized whole, and Tesseract's own layout gives the reading order. A region of up to 2 megapixels at 2× is always a single pass.
- **Bands:** a larger scaled image is cut into horizontal bands of about 2 megapixels (measured: half the time and two thirds of the memory of 8-megapixel bands), recognized in order. A band never exceeds 8 megapixels after scaling, overlap included.
  - Each cut goes at the last blank row gap in the final quarter of the band, so a gap only ever shortens a band.
  - With no gap there, the cut is made at the limit and the next band starts earlier by twice the estimated line height, and by no more than a quarter of the band. Every band starts strictly below the one before. Words found in both bands are merged by box overlap, keeping the higher confidence.
  - When a band would be shorter than four text lines (a very wide image), the scale drops to 1×. If it still would be, the input is refused with `input_excessive`.
  - Reading order for a banded image is band by band, top to bottom, with Tesseract's order inside each band. The result says `banded: true`.
- **Languages:** at most three per job, and at most 64 MiB of data files in all. A language that a data file pulls in by itself counts toward both. Over either limit the job fails with `language_unavailable`.
- **Budget, with the shipped English data:** peak RSS for the whole job under 128 MiB for any accepted input. The helper recognizes in parallel, one engine per thread and at most four, and starts another engine only while its resident set stays under that budget; a dense 1-megapixel region measured 101 to 103 MiB on four threads. (The separate 80 MiB figure first planned for small regions is withdrawn: the helper is transient, and the memory buys the speed bar.) With other data the budget grows by the size of the data files beyond English, so 192 MiB at most. The `RLIMIT_DATA` ceiling in decision 2 is set from the same figure; the RSS budget is what acceptance measures.
- **Time follows the characters recognized, not the pixels** (measured on m74: 0.55 to 1 ms per character, on Tesseract 5.3.4 and 5.5.0 alike). A 24-megapixel page of dense text, about 100,000 characters, needs 54 s or more, so no pixel cap brings every accepted input inside the deadline.
- **Time budget.** Recognition therefore has a time budget inside the deadline. When it runs out, the job stops and returns what it has recognized so far, in reading order, with `truncated` true; the notification and the editor say the text was cut. It never fails a job that has text to give. (Decided by the coordinator on 2026-11-12 while Patrick was away; listed under open decisions.)
- Spawn, engine start, recognition and copy are timed separately in every receipt, so a missed bar shows where the time went. If the 1 s bar is missed on engine start alone, the helper may be started when the region selector opens and killed on Escape; it still never outlives its job. Item 4b builds that only if this measurement calls for it.

### 4. Recognition quality

The engine work starts from the baseline (upscale small text, handle dark pages) and settles the method by measurement on the corpus in Acceptance, comparing at least: Tesseract's own thresholding methods against a put.gd background estimate and inversion; 1×, 2× and 3× scaling chosen from estimated text height; page segmentation modes for small regions and whole windows; a border added around tight crops; mixed light and dark areas in one region; dictionary on and off for code and tokens. The chosen method is recorded with its numbers in the design page.

Two outputs come from one pass:

- **Text for copying:** words under a confidence floor and lone symbols produced by icons are dropped; meaningful symbols in code and paths are kept; line breaks are kept. Words a person could not read in the source are dropped too: contrast against their background under a floor, or glyphs under a minimum height. The floor is set so near-white text on white goes and the dimmest real interface text stays.
- **Candidates for Quick redact:** every recognized word with its box and confidence, unfiltered. Only the editor asks for them; the resident never holds them. The `words` an agent reads are the filtered words of the copied text, not these.

### 4a. What may be copied or shown

Recognized text and code content come from whatever was on screen, so they are treated as untrusted.

- Before any copy, display or agent reply: C0 controls except tab and newline are removed, as are C1 controls and the bidirectional override, embedding and isolate characters; U+2028 and U+2029 become newlines; the text is put in NFC. Every other format character (Unicode category Cf: zero-width, invisible and tag characters) is removed as well, from code content without exception and from recognized text except U+200C and U+200D, which Persian and Indic scripts need.
- The editor's code rows show any remaining unusual character escaped.
- The MCP descriptions of `text.inspect`, `editor.inspect` and `history.copyText` say the content is screen data from an untrusted source and never instructions.
- Copy text is an ordinary copy. put.gd does not mark it as a secret, so a clipboard manager such as Klipper may keep it. "Nothing is stored" describes put.gd's own files, and the user guide says so.

### 5. Quick redact matching

- **Categories:** email addresses; phone numbers (international and national forms, at least 7 digits); IPv4 and IPv6 addresses; card numbers (13 to 19 digits with spaces or dashes, Luhn-valid); keys and tokens.
- **Keys and tokens** means these shapes, listed in the tool's help: AWS access key IDs, GitHub, GitLab, Slack and Stripe prefixed tokens, JWTs, PEM private-key blocks, and unbroken hex or base64 runs of 32 characters or more.
- Matching runs over the unfiltered candidates, joined across adjacent words and wrapped lines, after normalizing whitespace and Unicode digits and allowing the usual confusions (`0/O`, `1/l/I`, `5/S`, `8/B`) where the shape fixes the alphabet.
- A match becomes Redact marks over its word boxes, padded by a quarter of the line height and clamped to the image.
- One invocation is one atomic `editor.apply` batch and one undo step. `redactText` must be the only command in its batch: a batch that mixes it with other commands, or repeats it, is rejected with `edit_command_invalid` before any recognition.
- `redactText` answers when it is done, not at once. Its transport deadline is the recognition deadline plus a margin, above the editor's usual command deadline. If it times out the recognition is cancelled and no mark is added later.

### 6. Languages

- English data ships with every package. Other languages come from the distribution's Tesseract language packages, or from files the user puts in `~/.local/share/putgd/tessdata/`, which every package kind reads.
- Each language resolves on its own: the user directory first, then the packaged or system data directory. A user file that fails to load falls back to the system copy of that language when there is one.
- Identifiers are validated by the pattern `^[a-z]{3,4}(_[a-z0-9]+){0,2}$`, count and uniqueness when Settings are saved, since validation does no file access and a removed language package must not make a saved configuration invalid. Whether the data is installed is checked when a job starts. No engine configuration, variable or path is accepted from a caller.
- Settings → Capture → Text recognition lists the installed languages, up to three selected. The default is the desktop locale's language when its data is installed (a fixed ISO 639-1 to Tesseract table), then English.
- A language named in a `languages` parameter that cannot load fails the job with `language_unavailable` naming it. A language from Settings that cannot load is skipped when another loads; the result lists `languagesUsed` and `languagesSkipped`, and the notification adds "(German data is missing)".
- The list comes from the resident reading the names and sizes of `*.traineddata` files in fixed directories, which loads no engine and starts no helper: `/usr/share/tesseract-ocr/5/tessdata` (Debian, Ubuntu, Mint), `/usr/share/tesseract/tessdata` (Fedora), `/usr/share/tessdata` (Arch), the AppImage's own directory and the user directory. Files that are not languages (`osd`, `equ`) are left out of the list. The helper validates a file when a job loads it. Engine versions come from the build manifest. Quality receipts record each data file's name, size and SHA-256.
- put.gd does not download language data.

### 7. The operation, the journal and the clipboard

- **A new route-free action kind.** `text` is in `invocableActionNames()` with a hotkey. It has no destination, archive or naming, is not in Per-action exceptions, and is exempt from `output_required`. Schema-1 normalization adds it with an empty hotkey; the config schema, `Settings::validate`, `ViewState` and the diagnostics bundle learn it. The language list is a new validated `preferences` key. As with every action added before it, a configuration written by this build is not accepted by an older build; that downgrade limit is unchanged.
- **States:** `accepted` → `acquiring` → `recognizing` → `completed`, `cancelled` or `failed`. Acceptance is journaled exactly as for a capture on that adapter: operation ID, action, configuration revision and the two durable checkpoints. Recognition never starts before both. The journal holds states and the terminal outcome (character and code counts, or an error code) and nothing recognized.
- **Recovery:** `HistoryStore::recover` marks an operation found in `recognizing` as `interrupted` with `text_interrupted`, as it does for `editing` and `recording`. One found in `accepted` or `acquiring` gets `source_interrupted`, as any capture does. Neither is rerun.
- **Completion:** a `text` operation has no items and does not go through the upload completion path (`performCopy`, posters, upload copies). It has its own completion branch.
- **Journal size:** a completed or cancelled `text` operation's row is deleted when it reaches that state, so a much-used action does not grow the journal. Failed and interrupted ones stay.
- **History:** a completed or cancelled `text` operation is not listed. A failed or interrupted one is listed as "Text recognition failed" with its reason and no retry, like Capture failed.
- **Clipboard:** the write goes through `deliverCopy` as an explicit copy. It takes the explicit-copy ticket and the expected clipboard revision at acceptance, advances the upload-copy epoch, and is suppressed if the user changed the clipboard after acceptance. The outcome is `copied`, `suppressed` or `failed`, reported to the caller and in the notification. `copy: false` skips the write and the notification entirely. The same rule covers the editor's text and code copies, History's Copy text and the QR image copy.
- **Result retention:** the interactive action and History's own Copy text ask the helper for text and codes only, and keep nothing but counts. An operation started by `text.recognize`, or by `history.copyText` with `keepResult` true (the CLI and MCP forms), keeps its result in the resident's memory for the agent, at most 4 MiB in all: the text first, then codes, then as many words as fit, with `truncated` true when anything was cut. It is held as one compact byte array, never as a parsed tree, so freeing it returns the memory, and the resident asks for heap reclamation when it goes. It is kept until the next recognition is accepted, 120 s pass, or the resident exits. It is never persisted and never in a UI checkpoint or diagnostics. After that, `text.inspect` answers with `resultExpired: true`.
- **Terminal record:** the resident keeps a small in-memory record of the last 32 text operations (state, counts, `copyStatus`, error code), which is what `text.inspect` answers from once an operation ends, for every kind of start. An older or unknown ID is `operation_not_found`. It holds nothing recognized.

### 8. Sources for `text.recognize`

| Source | How it is acquired |
| --- | --- |
| `region` | The native selector, exactly as the action does. There is no rectangle parameter: an agent that knows an area uses `monitor`, `window` or `desktop` and filters `words` by box |
| `window`, `monitor`, `desktop` | The adapter's `prepareAcquisition` for that source: identity is frozen and pixels are read at the same points as for a capture on that adapter today, including where an adapter starts its capture inside preparation (KDE's window capture). This feature changes no adapter's acquisition timing. A source an adapter cannot capture reports that adapter's own capability error |
| `clipboard` | An image on the clipboard, or exactly one copied local PNG or JPEG file, reserved as a clipboard import is. Anything else is `source_unsupported` |
| `file` | An absolute path to a local regular PNG or JPEG file, decoded through the image worker |
| `history` | The item's retained local copy only |

The interactive sources hold the one interactive-acquisition slot (`busy_selecting`). The resident runs one text operation at a time, counted from acceptance: a second request is refused with `text_busy`, so a job never waits behind another one's region selection.

### 9. Agent contract

Every interactive capability has a session method, a `putgd-cli` form and an MCP tool with strict validation (`additionalProperties: false`) and a parity test. The contract commit encodes this table in a schema file with fixtures; it does not make new decisions.

| Method | Parameters | Returns |
| --- | --- | --- |
| `action.invoke` | `action: "text"`, `delaySeconds?` | `operationId`; copies |
| `text.recognize` | `source` (decision 8) with `path` only for `file` and `historyId` only for `history`; `languages?` (1 to 3 installed identifiers); `copy?` (default false); `delaySeconds?` for the screen sources | `operationId`, `state` |
| `text.inspect` | `id` | `state`; when completed: `text`, `words[{text, rect, confidence}]`, `codes[{format, kind: "text" \| "binary", text?, length, quad}]` in source pixels, `truncated`, `banded`, `languagesUsed`, `languagesSkipped`, `copyStatus`, `resultExpired` |
| `text.cancel` | `id` | the terminal state |
| capabilities | none | a `text` block: `available`, `error` with the install hint or the missing confinement, engine versions, `languages`, and availability per source. It starts no helper |
| `editor.recognize` | `id` | starts recognition for the current revision; `editor.inspect` gains `text {state, result, words, codes, selection}` with the same bounds. `result` identifies one recognition result and changes with every new one |
| `editor.selectText` | `id`, `result` (the result identity from `editor.inspect`), `from` and `to` (word indexes in reading order), or `all`, or `none` | the selection; `editor.inspect` reports it. A `result` that is no longer current is refused with `edit_stale` |
| `editor.copyText` | `id`, `result`, `all?` (default false: the current selection) | `copyStatus`, character count; a `result` that is no longer current is refused with `edit_stale` before anything is copied |
| `editor.apply` op `redactText` | `categories[]` (1 to 5 of the names in decision 5) | created shape IDs and counts per category |
| `editor.copyCode`, `editor.openCode` | `id`, `result`, `index` | `copyStatus`, or the launch result; open launches at once and is refused for anything but a valid http or https URL |
| `history.copyText` | `id`, `keepResult?` (default false) | `operationId`; follows `text.inspect` |
| `history.qr` | `id`, `mode: "copy" \| "save" \| "show"`, `path` (absolute, required for save only), `overwrite?` (default false) | when the receipt refresh and the copy or write finish, under Copy link's deadline: `copyStatus`, the saved path, or the window state. Save fails on an existing path unless `overwrite` is true, as the editor's Save a copy does |

A parameter that names an operation is spelled `id`, as in every existing editor, recording and history method. The recognition methods reply at once and are followed through `inspect`, as for scroll and recording; `redactText` is the exception (decision 5). `history.qr` has no operation: it holds its reply until it is done, as Copy link does.

### 10. Codes

- All decoded codes are returned ordered top to bottom, then left to right, by the centre of their quadrilateral. Rotated and skewed codes report their quadrilateral.
- Content that is not valid text (binary, or bytes that do not decode as UTF-8 or the code's declared charset) is reported with `kind: "binary"` and its length only, to users and agents alike. It is neither copied nor shown and does not count as a code in the notification; a region holding only binary codes ends as "No text found".
- One code that fails to decode does not fail the job.
- **Opening** exists only in the editor's code line: http or https, no control characters, at most 2,048 characters; user-info in the URL is shown, not hidden; a launch failure is reported.
- **Writing:** the link is exactly what Copy link would copy now, after the same receipt refresh. Error correction exactly M (`boostEcl` off), a 4-module quiet zone, integer module scaling, black on white in both themes. The window draws the code at the largest whole number of pixels per module that fits its code area (560 px square by default, growing with the window), never under 3; the largest code, 185 modules with its quiet zone, is then 555 px. Copy image and Save produce a PNG at the smallest whole scale that reaches 1,024 px, whatever the window shows. A link too long for a QR code at level M (over 2,331 bytes) is refused with `qr_too_long`.

### 11. Packaging

| Target | Runtime packages | Build packages | ZXing |
| --- | --- | --- | --- |
| Ubuntu 24.04, Mint 22 | `libtesseract5`, `tesseract-ocr-eng`, `libzxing3` | `libtesseract-dev`, `libleptonica-dev`, `libzxing-dev` | 2.2.1 |
| Ubuntu 26.04, Debian 13 | the same | the same | 2.3.0 |
| Fedora 44, 45 | `tesseract-libs`, `tesseract-langpack-eng`, `zxing-cpp` | `tesseract-devel`, `leptonica-devel`, `zxing-cpp-devel` | 2.2.1 |
| Arch | `tesseract`, `tesseract-data-eng`, `zxing-cpp` | the same | 3.1.1 |

- These are hard dependencies: the helper links the libraries, and one complete package is the house rule. The reading code uses only `ReadBarcodes(ImageView, ReaderOptions)`, present in 2.2.1, 2.3.0 and 3.1.1, with the result type inferred because its name changed. Every package build proves it compiles and links. Fedora 45 and Aurora install the Fedora 44 RPM, as they do today, so its dependencies are checked there in package acceptance. Mint's names are inherited from its Ubuntu base and confirmed in package acceptance.
- **AppImage:** builds Leptonica (no image-format libraries at all), Tesseract (LSTM only, no curl, no archive, no OpenMP, no training tools) and ZXing-cpp (readers only) from pinned sources, cached by source, configuration and toolchain hash, and carries English `tessdata_fast` pinned by commit and SHA-256. This adds no codec or network library to the image beyond what Qt already bundles. It does not bypass the CVE gate: the three engines and the data join `bundled-components.json` with SBOM identities and CPEs, complete-source collection, configure recipes, notices and the exact-asset audit. Relocation and helper identity are tested from the mounted image. Grype matches Leptonica and Tesseract by name whatever is compiled in, so findings in code that is not built get an acceptance in `packaging/sbom/policy.json` with the configure recipe as evidence, as FFmpeg's do, and the stable CVE scan is rehearsed on d69 before the integration pull request merges, because pull-request CI skips it.
- `PUTGD_OCR` is `AUTO` for developer builds, like `PUTGD_RECORDING`, and required in every package build: a package build without the libraries fails. At run time a missing helper or missing English data reports `engine_unavailable` or `text_helper_missing` with what to install; the actions stay visible and say why they are off.
- **Latest versions.** Everything this feature pins for the AppImage starts at the newest upstream release on the day it is pinned, and the packaging pull request records the check. As of 2026-11-12 that is:

  | Component | Version | Released |
  | --- | --- | --- |
  | Tesseract | 5.5.4 | 2026-10-28 |
  | Leptonica | 1.87.0 | 2025-12-24 |
  | ZXing-cpp | 3.1.1 | 2026-07-29 |
  | English `tessdata_fast` | the repository head, `874164186573` (its newest tag, 4.1.0, holds the same `eng.traineddata`, unchanged since 2017) | 2024-08-01 |
  | QR Code generator (vendored, every package) | v1.8.0 | 2022-04-17 |

  The source pins go in `packaging/appimage/tools.lock.json` beside FFmpeg and QtKeychain, with their tag commits derived by `tools/maintenance/refresh_pins.py`, and each gets a Renovate rule in `.github/renovate.json` so it keeps moving: patch releases open at once, a new minor or major waits for approval, as FFmpeg's do. Any new build tool the feature needs follows the same rule. The native packages use whatever each distribution ships (decision 11's table); the helper is built and tested against both ends, 5.3.4 with ZXing 2.2.1 and 5.5.4 with ZXing 3.1.1.
- Size targets, provisional until measured: under 12 MB added to the AppImage, about 12 MB of new packages on a native system with none of them.

### 12. GNOME

- `text` joins the extension's hotkey list, so the packaged extension becomes version 23.
- As with every extension update, a session that still has version 22 loaded must log out and in once. Until then `GnomeAdapter` refuses region preparation (`helper_outdated`), so Copy text from a region reports the existing "log out once" step, as Capture region and region recording do. Every existing gate keeps its present version rule (scrolling capture stays available from version 22), and this feature adds no compatibility path.
- With version 22 loaded, `text.recognize` from `window`, `monitor`, `desktop`, `clipboard`, `file` and `history`, the editor tools and History's actions still work, because they need nothing new from the extension.
- Tests cover version 22 loaded with 23 installed, and the restore of every shortcut after login.

### 13. Where the controls go

| Surface | Decision |
| --- | --- |
| Command band | "Copy text", after Capture scrolling region and before Upload clipboard. Narrow label "Text". A new IconArt glyph `copy-text` (a letter T inside selection corners). It is a secondary command: icon-only from the stage where Capture scrolling region is, and the band's minimum width is recomputed from the last stage |
| Its tooltip and accessible text | "Select a region and copy the text in it. Nothing is saved or uploaded." It shows no output line; its unavailable badge follows the region source and the text engine |
| Tray, both implementations | "Copy text from region", directly after Capture scrolling region. The native menu appends ID 41 and has no output row for it. The menu closes when it is chosen, as for a region |
| Settings → Hotkeys | A row "Copy text from region" after Capture scrolling region; `shortcutOrder()` gains it there. `presentationOrder()` does not, because it has no output |
| Capture output summaries | Never list it |
| History | **Copy text** in an image item's inspector and ⋯ menu, beside Edit again. **Show QR code** beside Copy link |

### 14. Region acquisition on each desktop

`text` acquires exactly as `region` does, and each adapter's early paths, which today name `region` and `edit`, learn it:

| Desktop | What must treat `text` as a region |
| --- | --- |
| Cinnamon X11 | The early crosshair in `X11CoreSourceAdapter`, in both the live and the screenshot-first mode |
| GNOME | The extension's map from an action to its region preparation, and the adapter's prepared hotkey tickets, which are indexed by action |
| KDE | The `putgd-region` selector, its cleanup, and the transparent-frame fence before ScreenShot2 |
| Budgie | The same, with Budgie's presentation-based lock witness |
| Hyprland | The early press catcher in `HyprlandSourceAdapter` |

- Delay ordering (selection first when live, countdown first when screenshot-first) and the "Also delay captures started by a hotkey" preference apply unchanged.
- A text capture never changes the rectangle that Repeat last region remembers.
- Where a selector says what the capture will do, it says "Copies text".

### 15. Feedback

A desktop notification through the resident's existing path, sent after the native clipboard acknowledgement. No new on-screen surface: the result carries no controls, so nothing is lost when notifications are off. While recognition runs, the tray shows the usual activity state.

## Performance and memory

| Rule | Check |
| --- | --- |
| No binary but `putgd-ocr` needs libtesseract, libleptonica or libZXing | The new rule in the native and AppImage package audits, on every package build |
| The resident never loads them, or libcurl or libarchive, at run time | After a workload of 20 `text.recognize` monitor jobs and 5 driven region actions, and a 180 s wait, that resident's `/proc/<pid>/maps` is checked against the idle forbidden-library list plus these names, on all five desktops. libgomp is not on the list: Qt Core already brings it into the resident through libb2 on Debian 13, Ubuntu 26.04, Mint 22 and Fedora 44 |
| Idle resident RSS and PSS stay under 40 MiB after that workload, with every helper's exit recorded | Gate C on the same resident, using the frozen evaluator |
| The agent result cache is bounded | Resident RSS 60 s after a `text.recognize` of the largest result, against the same point without it: growth under 8 MiB, and gone after 120 s |
| `putgd-ui` startup and its mapped libraries are unchanged | A/B of main-window and `--edit-image` open time and library list against the nightly head |
| Helper peak RSS within the budgets of decision 3 | Measured in every cell, including a dense 24-megapixel input |
| From the end of the selection to the clipboard acknowledgement: p95 under 1 s for a region up to 1 megapixel, and under 3 s for the corpus's full 4K monitor captures at the scale the method picks | 30 runs on m74 and on d69, native package and AppImage; 5 runs in every other cell |
| The hotkey-to-selector time of the other captures does not change | A/B with the existing hotkey latency probe |
| No recognition without an explicit action, no warm daemon | By design; the helper exits after one job |
| AppImage growth under the size target | Compared with the nightly head |

## Acceptance

Run on the exact candidate build with receipts, from a dispatched CI run on the integration branch at a recorded commit.

A cell is one desktop with one package kind: Mint Cinnamon/X11 (m74), Fedora GNOME/Wayland (f44), Ubuntu GNOME/Wayland, Kubuntu Plasma/Wayland (k72), Debian Plasma/Wayland (d69), Aurora, Budgie on labwc and Hyprland, each with its native package, and the AppImage where the acceptance matrix has an AppImage row. The matrix's GNOME/X11 and KDE/X11 rows get the pipeline check only (hotkey, paste witness, helper exit).

- **Real targets first.** On each of the five desktops, in light and dark, at 100 % and one fractional scale: a terminal showing a known file, a browser on a known local page and on live pages (a GitHub pull request, a Wikipedia article), a text editor with code, a chat or settings window with small text, and a full 4K monitor. The captures are taken once, with the current nightly's region capture, and stored with the receipts. The reference is a transcript of the text visible in the captured region: cut from the known source for local targets, and written and checked by hand once for live pages.
- **Quality is scored per engine build, not per desktop.** On fixed images the result depends on the Tesseract build and its data, not on the compositor. The stored corpus is scored offline against each engine build put.gd ships with: Ubuntu 24.04 and Mint 22, Ubuntu 26.04, Debian 13, Fedora 44 and 45, Arch, and the AppImage's own. The desktop cells then prove the pipeline: hotkey to paste witness, memory, helper peak and exit.
- **Text bars, per engine build and per target class, never pooled:** median character error rate at most 2 % for body text of 11 px and larger, at most 5 % for smaller interface text. Sizes are the font's pixel size in the captured image. Each class has at least 200 words from each desktop, and an engine build's score for a class pools those five desktops' captures. Text is compared after Unicode NFC and with runs of whitespace collapsed, case-sensitively. URLs and email addresses of 11 px and larger match exactly at least 90 % of the time. A second language (German, from the distribution's package) meets the body-text bar on one engine build. These bars are targets: the engine item measures them first. If a bar cannot be met after the method is settled, the numbers go to Patrick before anything merges.
- **Hidden and hostile content:** a page with near-white text on white and with 3 px glyphs (not copied); codes and text carrying control, bidirectional-override and zero-width characters (removed as decision 4a says); a small code inside a page image.
- **Limits and bands:** a 24-megapixel image; the same with three languages loaded; a very wide image; an image over the limit; a dense image with no blank row at any cut (no line lost or doubled at a seam); a tall two-column page (order is band by band, as documented); a code larger than a band.
- **Quick redact:** a synthetic page of fake emails, phone numbers, addresses, card numbers and tokens at 11 px and larger in four fonts, light and dark: every item is covered. A page of ordinary prose and a page of code, built to contain no item of any category: at most one redaction per page. A third page of hashes and identifiers that match the long-run rule by design: each is redacted, and that is the expected result. The confusions tolerated are fixed by fixtures. The exported PNG holds no original pixels under the marks.
- **Editor privacy:** a word under a Redact mark added, moved or restored by redo after recognition cannot be selected, copied or returned by `editor.inspect`; a late result for an old revision is rejected.
- **Codes:** QR from 3 px per module to full screen, light and dark, versions 1 to 10 and one version 40, rotated, on a busy background, several in one region; Micro QR, Data Matrix and Aztec; URL, Wi-Fi, contact, plain and binary payloads. Show QR code and its saved PNG are read back by two independent decoders (ZXing's and zbar's command-line tools), for a short link, a long presigned link and the longest allowed link.
- **Privacy:** with debug logging on, canary strings recognized in a capture appear nowhere in the journal, the History database, logs, notifications, UI checkpoints, a diagnostics package or any file under `/tmp` and the runtime directory; pixels of a screen capture appear in no file either. A completed text operation leaves no journal row.
- **Clipboard:** a user copy made during recognition is not overwritten; a pending upload link does not overwrite the text; a later explicit copy supersedes it; `copy: false` leaves the clipboard alone. Multi-line Unicode text pastes intact, PRIMARY is untouched, and the text still pastes after the editor closes, after the resident quits (through the clipboard keeper on Budgie and Hyprland, which then exits when another application copies) and after an AppImage is unmounted.
- **Helper failures:** crash, hang past the deadline, each resource limit reached, cancel, wrong build, wrong protocol, corrupt or missing data, confinement refused, the parent killed mid-job. Each ends in its fixed error with the exact child and any thread of it gone, and no recognized text or screen pixels on disk.
- **Confinement:** from inside a test build of the helper, each of these fails: opening a socket, executing a program, starting a child process, writing a file in the home directory, reading a file outside the allowed directories, reading another process's memory. It is tested on a first recognition and on later bands, with the distribution's OpenMP build, and the Landlock ABI is recorded for every target.
- **Every desktop:** driven through the real hotkey, tray and window button with an independent paste as witness.
- **Unavailable paths:** helper or data missing; version 22 of the GNOME extension loaded; each source on each desktop against that adapter's capability report; a locked screen; a History item with no local copy.
- **Packages:** a clean install of each target with recommended and weak dependencies turned off still has the engine and English data; an upgrade from the previous nightly through the signed apt, dnf and pacman repositories; a rebuild from the extracted source archive, which must hold every vendored and provisioning input; the recording Recommends unchanged; the native audit and the AppImage audit cover the helper and the vendored generator's notice. Fixed critical or high CVEs in bundled code warn on a nightly and block a stable release, as `docs/release/release.md` says.
- **Window sizes:** the command band at the window's minimum width and at enlarged text, in the UI catalog and on one desktop.

## Work items

| # | Item | Depends on |
| --- | --- | --- |
| 1 | Documentation A: lift the non-goal in `AGENTS.md` and the two design pages | none; merges first |
| 2 | Contract commit: the core job class and its fake backend, the helper protocol and its fixtures, the resident's recognize, result and copy interface that the action and History both call, every new session method registered and answering `not_implemented`, the MCP tools and parity tests for them, the settings and journal shapes, the build option and an empty `cmake/Ocr.cmake` | none |
| 7 | Corpus and harness: the real-target capture set taken now with the current nightly, transcripts, error-rate and latency tools, the synthetic redaction, code and hostile pages, the post-text memory workload and maps check | none; starts with 2 |
| 3 | Engine: `putgd-ocr`, memfd transfer, confinement, bands, recognition method, codes, limits, helper failure tests | 2; settles its method on 7's corpus |
| 4a | The resident: settings and schema, dispatch, journal, clipboard, notifications, `text.*` methods, CLI, MCP | 2 |
| 4b | The desktops: the five region paths, GNOME extension 23, hotkeys, tray, command band, Settings page. It holds one desktop lock at a time | 4a |
| 5 | Editor tools and Quick redact, History's Copy text and Show QR code, the vendored QR generator, their agent methods | 2 |
| 6 | Packaging: DEB, RPM, pacman, AppImage source builds, notices, SBOM, audits and the new audit rule | 2; finishes after 3 and 5 |
| 8 | Measurement and desktop acceptance on one complete candidate | 3, 4b, 5, 6, 7 |
| 9 | Documentation B: design page `docs/design/text-recognition.md`, user guide, errors, CLI, MCP, desktops, acceptance matrix, release | 3, 4b, 5, 6; merges after the code |

**First light comes before breadth.** It needs the contract commit, a minimal engine (default Tesseract settings, no bands), item 4a, item 4b's Cinnamon and Plasma slices (the region path and the hotkey on those two) and item 6's DEB dependencies, and those are built first. As soon as they exist, a native DEB built by CI for a chosen commit of the integration branch goes on m74: the real hotkey, a paste witness, the helper's peak RSS and exit, and the resident's maps afterwards. Then the same on d69. Items 5 and 6 must not be half done before that result exists. The AppImage follows when item 6's source builds are in, since editing `packaging/appimage/*.json` rebuilds the 224 MB source cache.

**One integration branch.** All feature code lands on `feat/text-recognition`, and one pull request takes it to `nightly` after acceptance, so no nightly ships part of the feature. Item pull requests target that branch. The integration pull request is opened as a draft right after item 2. Its CI run is cancelled by every new push and builds the merge commit, so lab candidates come from a manually dispatched CI run on the branch at a chosen commit, or from a Boat candidate build (`docs/lab/boat-candidates.md`).

**Who owns shared files.** After the contract commit, each item fills in only its own handlers and files:

| Files | Owner |
| --- | --- |
| `Settings.cpp`, the config schema, `OperationService` dispatch, `OperationClipboard.cpp`, `HistoryStore::recover` and the journal, `LocalServer.cpp` registration, `tools/mcp/share_mcp/server.py` | item 4a |
| `src/platform/`, `integrations/gnome/extension.js`, the tray, the command band, the Settings page | item 4b |
| `src/ocr/`, `cmake/Ocr.cmake`, and after item 2 creates them: the text-job protocol library, the `check_layers.py` entry and the `ProductBinaries.cmake` line | item 3 |
| `src/editor/`, `EditorWindow.cpp`, `src/ui/ImageEditor.cpp`, `HistoryWindow.cpp`, `HistoryService`, the vendored generator's directory | item 5 |
| `packaging/`, the dependency lock, notices, SBOM and release tools, `audit_native.py` | item 6 |
| `tests/performance/`, the corpus and lab tools, the memory workload | item 7 |

An item that needs a line in another owner's file asks that owner.

## Open decisions for Patrick

None of these blocks the start.

1. **A default hotkey for Copy text.** The plan leaves it unassigned, like every action added after the first three.
2. **Quick redact stays or goes.** The plan keeps it. One council reviewer would cut it as a separate feature whose misses are a safety risk; cutting it removes decision 5, the unfiltered candidates and three acceptance pages. Item 5 builds it last, so a cut costs nothing if it comes early.
3. **Speed on the slowest builder.** The first numbers reported from m74 were from a debug build and were wrong. With a release build and parallel recognition, the helper alone takes 0.99 s for a dense 1-megapixel region at 2× and 2.88 s for a 4K page of interface text on m74, against bars of 1 s and 3 s, at 101 to 105 MiB peak. Those are helper times, before the grey conversion and the clipboard write, so the end-to-end bars are close and are settled by the acceptance run. If they are missed there, the numbers come to you before the feature merges.
4. **Very long text.** A capture with more text than the deadline allows returns what was read, marked as cut, rather than failing. Say so if you would rather it failed.
5. **The nightly desktop check.** Adding the engine libraries to the frozen Tier 1 Idle memory cell's forbidden list is a one-line harness change. The plan does not need it (the package audit and the post-text maps check cover it), so it waits for a yes.

## Out of scope, as final decisions

- Searching History by the text inside captures, and any recognition that runs without an explicit action.
- In-app language downloads.
- Translation, and AI description of images.
- Handwriting, linear barcodes and PDF417.
- Opening a link from the Copy text action or from a notification.
- A rectangle parameter for region recognition, and a compatibility path for an outdated GNOME extension.
- Global multi-column reading order for images large enough to be banded.
