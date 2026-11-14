# Round 3: GNOME on f44

Fedora 44, GNOME Shell 50.6, native Wayland, physical f44 (192.168.68.70). Candidate RPM from completed successful CI run 43626107441; [diagnostics.build](a/build.json) confirms commit `57a8749739583638bf991c925d49f7e850608830`, full tree `06cb312233f9a0155419f99c92db3e0277138c88`. Published nightly control is `v26.1113.4757-nightly`, commit `466449a4c69a07a1997668d1b70d637abac76a16`, tree `4346aa6ecf750b5cceb4dcedf6c10e5c11279ad3` ([diagnostics](b/diagnostics.json)). Real GDM re-logins loaded each package's extension, versions 23 and 22 respectively. Browser was our private Firefox on the public Linux Wikipedia page; save locally only, no upload or copied link. Native helper debug logs are [candidate](a/helper.log) and [nightly](b/helper.log).

| Row | Result | Observation |
|---|---|---|
| G1 relative correction | Pass | A separate randomized probe caused `pointer put back by 6,0 sent`; no relative refusal or absolute correction fallback anywhere in candidate log. |
| G2 first-click trials | 5 failed first clicks; nightly also fails | Candidate fixed **6/10**, random **9/10**, all 20 paused. Round 2 was fixed 8/10, random 10/10. Current published nightly fixed **0/10**, random **0/10**, no pause on any try. Open-loop counts remain informational under the inherited round-2 rule; the random >=9/10 fallback threshold is met. Report the misses, not the later API Stop, as first-click failures. |
| G3 Resume/input/performance | Pass | Static pair 6792 px, identical PNG SHA and all 64-row bands. Pointer pause quiet; real terminal click and `abc` received. Untouched Linux captures both end_of_content: 23734 px, 60 steps, 24.449 / 23.852 s. |
| G4 duplicate session Resume | Pass | Second request returns `scroll_state`; original capture continues to end_of_content, 6792 px, image retained. |

## G1 correction evidence

`a/correction-probes.jsonl`: `g1-random-14`, operation `937030d2-9b88-4b3f-9fdf-d3ad819226a0`, randomized start 4580 ms, pause 91.092 ms, two ordinary later pointer commands, one correction; first click stopped it. Exact helper line:

```
2026-11-14T12:51:50.055 scroll inject: t=327068 pointer put back by 6,0 sent
```

This is a successful relative call, rather than inference from an unchanged cursor: at the tested head [MutterScreenCast.cpp](https://github.com/patrick-hudson/put.gd-desktop/blob/57a8749739583638bf991c925d49f7e850608830/src/record/MutterScreenCast.cpp) calls `NotifyPointerMotionRelative` and reports refusal on D-Bus error; [ScrollCapture.cpp](https://github.com/patrick-hudson/put.gd-desktop/blob/57a8749739583638bf991c925d49f7e850608830/src/record/ScrollCapture.cpp) emits `pointer put back by ... sent` only when `movePointerBy` returns true. The absolute fallback has a distinct `pointer put back at` line. Neither that fallback nor `relative motion refused` occurs in the candidate log. Standard G2 trials happened not to cause corrections; all 14 separately labeled randomized correction probes are retained, without replacing those trials.

## G2 details and failures

[Full per-try tables](tries.md) and raw [fixed](a/tries-fixed.jsonl) / [random](a/tries-random.jsonl). The failed first clicks were fixed 1, 2, 6, 9 and random 8; pause delays 50.899, 52.772, 102.413, 82.434 and 92.282 ms respectively. Each had two ordinary pointer commands after the first motion and zero corrections. No causal claim is made from this small sample. Published nightly fails every corresponding fixed/random trial ([fixed](b/tries-fixed.jsonl), [random](b/tries-random.jsonl)); pointer injection continues, often losing track, and the driver uses its explicitly recorded later API Stop when needed. These are not failures unique to the PR, but candidate results declined relative to round 2.

The driver uses the author's uinput mouse, flat acceleration, 6 pixels per 10 ms; one initial tablet placement establishes the middle of the screen. All subsequent motion is relative. Each try's launch phase is randomized independently. The wall's absolute VNC pointer is not used for the path. Driver source and actual commands are retained under [setup](setup/).

## G3 and G4 artifacts

[Untouched times](a/s1.jsonl) are about the published nightly's 24.339–24.984 s measured on this same desktop in [round 2](../../gnome/b/s1.jsonl); those timing controls are from round 2, not newly collected timing controls. New round-3 nightly runs here are the G2 deliberate-motion controls. Both whole Linux images were inspected ([contact sheet](whole-image-contact-sheet.png)).

Static [untouched](a/pointer-plain.json) and [resumed](a/pointer-resumed.json) results: same SHA `b7fd2b04e7870f388733b80a02fb2ccdd38e70170d9d4c96c9b759d2b204834d`; [band comparison](a/band-comparison.json) has no differing bands. [Paused bar](a/pointer-paused.png), [terminal typing](a/terminal-typed.png), [received text](a/terminal-received.txt), [quiet log](a/terminal-quiet.log). The static fixture avoids live-page rendering changes. [Duplicate Resume calls](a/double-resume-calls.jsonl) and [final image result](a/double-resume.json) retain the rejected second call and successful completion.

## Host restoration

Main lease `scroll1520-r3-gnome` released 19:01:12 UTC. A short verification lease `scroll1520-r3-clean-verify` released 19:03:19 UTC, after actual typing and final Shell verification. Both receipts are in [round-3 metadata](../metadata/). State found and restored exactly: enabled extensions `['background-logo@fedorahosted.org', 'putgd@put.gd']`; disabled `['hkwitness@lab']`; mouse acceleration `'default'`. No RPM was installed initially; test RPM and extension files removed. Final real GDM re-login performed. No test uinput device, helper, resident, application window, capture surface or notification remains. [Cleanup JSON](a/cleanup.json), [ordinary terminal input](a/r12-typed.png), [final empty Overview](a/r12-shell-final.png). A black-background VNC frame with live Shell panel was retained, then the final visible Overview established the desktop was live and empty; it was not treated as cleanup proof on its own.

RPM transactions were previewed/tested and scoped only to putgd. No desktop or compositor package changed. Existing offline-update queue was not applied or rescheduled; its previously observed invalidity is not claimed to have been repaired. Private browser/config directories are excluded from publication. Host-side source and verified export archive are retained.
