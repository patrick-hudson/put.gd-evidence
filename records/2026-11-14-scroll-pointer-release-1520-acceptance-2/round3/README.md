# Round 3: GNOME relative correction and Hyprland watch acceptance

Tested PR [#1520](https://github.com/patrick-hudson/put.gd-desktop/pull/1520), head **57a8749739583638bf991c925d49f7e850608830**, full tree **06cb312233f9a0155419f99c92db3e0277138c88**, from the finished successful manual CI run **43626107441**. Both desktops prove this identity through `diagnostics.build.gitTree`; the tree also matches GitHub's git-commit API. [Build/package identity and SHA-256](metadata/build-and-packages.json). This is a follow-up to the earlier accepted round 2 and m74 addendum, not a claim to have repeated other desktops on this head. Read PR description Round 3, issue #1514, author round-2 evidence, and the existing acceptance/automation/lab design before the checks. No product code changes, local builds, subagents, PR comment or merge.

## GNOME, physical f44

| Row | Result | Evidence / observation |
|---|---|---|
| G1 relative correction | **Pass** | One randomized correction sends `pointer put back by 6,0 sent`; no relative refusal or absolute fallback. |
| G2 fixed/random relative mouse | **First-click failures: 4 fixed + 1 random** | Candidate fixed **6/10**, random **9/10**; round 2 fixed 8/10, random 10/10. All 20 candidate tries pause. Current nightly fixed **0/10**, random **0/10**, no pauses. |
| G3 Resume, input, untouched timing | **Pass** | 6792 px pair byte-identical and equal in every 64-row band; terminal receives actual click and `abc`, zero paused injection. Two untouched Linux captures EOC at 23734 px, 60 steps, **24.449 / 23.852 s**, about prior nightly 24.339–24.984 s. |
| G4 duplicate session Resume | **Pass** | Second call refused with `scroll_state`; capture continues to EOC and retains the 6792 px image. |

[GNOME details, exact failed tries and restoration](gnome/README.md), [all per-try tables](gnome/tries.md). Five failed first clicks are explicit: fixed 1/2/6/9 and random 8. Each logs two ordinary pointer commands after motion, no correction. Delays are 50.899 / 52.772 / 102.413 / 82.434 / 92.282 ms. Nightly fails the same row on all fixed/random controls, so these are not demonstrated failures unique to the PR. The decline relative to round 2 remains reported.

## Hyprland, fresh guest h3 on f44

| Row | Result | Evidence / observation |
|---|---|---|
| H1 untouched Linux | **Pass** | Candidate **57.427 s / 51 steps**, nightly **73.746 s / 73 steps**. Both EOC, 22940 px, byte-identical PNG. No untouched lost_track. |
| H2 random relative mouse | **One failed first click** | Candidate **9/10**, all pause; trial 8 logs one later pointer command, zero corrections and misses. Nightly **0/10**, plus the matching-delay recheck also fails. |
| H3 Resume/watch and early pause/input | **Pass** | Actual GUI Resume matches untouched at 6672 px and in every 64-row band. Watch mapped during Resume quiet period and absent for both paused states. Real click moves focus Chromium→Foot and `abc` arrives in both. API pause sent **75.255 ms after start invocation**, before step 1. |

[Hyprland details and restoration](hyprland/README.md), [all per-try tables](hyprland/tries.md). Trial 8 pauses after 76.681 ms but misses the first click; later API Stop is not counted as success. Matching nightly delay yields no pause, 13 further pointer commands and `lost_track` at 720 px. This also fails on nightly, so it is not demonstrated to be a new PR regression. An initially overstated 10/10 progress count was corrected from the complete raw audit to 9/10; no candidate retry replaced the miss.

The inherited round-2 rule makes open-loop scores informational, with the >=9/10 random fallback threshold met on both desktops. The failed clicks are preserved as failures rather than silently marked successful. No new candidate-only failure was established by the nightly controls; the coordinator retains the acceptance decision.

## Method and final host state

Author's relative `/dev/uinput` driver, flat acceleration, ~600 px/s, one event per 10 ms. Fixed starts 2 s, random starts 1–6 s, with independent capture-launch jitter. GNOME uses one initial tablet placement only; Hyprland uses one initial relative jump computed from native cursor position. Subsequent motion is purely relative. Wall VNC absolute events do not drive the trials. Separate randomized GNOME bar-relative probes provoke the correction, without replacing G2 data. Those exploratory probes were 13/14 first-click stops: `g1-random-2` also missed (100.333 ms pause, 63 ordinary commands over the full post-motion/post-click observation, no correction). No matched nightly bar-start probe was run, so this extra miss is reported without PR attribution; the standard nightly random row is 0/10. Public Wikipedia in an owned private browser and a static synthetic fixture; local save only, no uploads or copied link. Screenshots and full PNGs are actual desktop output, inspected visually; no mock desktop evidence.

f44 GNOME: no putgd RPM was present initially and none remains. Packaged Shell extension tested after real GDM re-logins, then removed. Both saved extension lists and original mouse acceleration restored exactly before the last re-login. Final normal terminal click/key witness and empty live Overview observed. No own app, capture surface, notification or uinput device remains. Main lock released **19:01:12 UTC**, final verification lease released **19:03:19 UTC**; [receipts](metadata/). Native physical desktop is free. No other physical host was changed during this round.

Hyprland h3: resident, browser, terminals and final nightly clipboard keeper closed by session methods or exact verified PIDs; no remaining put.gd process/surface/window. Normal input witness succeeded, input configuration restored, exports verified. **Overlay retired at 19:24:55 UTC** by guarded `lab.py cleanup`, after a verified explicit completion manifest. [Retirement receipt](metadata/h-retirement/overlay-cleanup.json), [completion manifest](metadata/h-retirement/manifest.json). The `failed` manifest outcome conservatively preserves the first-click misses. Source golden and host-side evidence are retained. Only the owned guest wall tile/tunnel and owned preview tab were removed. No lease or running guest remains owned by this campaign.

Pinned strict-host-key SSH/scp throughout, including `BatchMode=yes`. New port pin remapped from the same golden's already authenticated host key. No SSH private key moved from workstation. No desktop/compositor package installed or updated. No `pkill -f`, pattern kill, or `rm -rf`. Failed setup attempts and corrected commands are retained in each desktop's setup/log artifacts. The pre-existing offline-update queue on f44 was not applied or rescheduled; its previously observed invalidity is not claimed to have been repaired.

## Retention and public evidence

[Verified bulk-export hashes and retained paths](export-checksums.json). Published candidate Hyprland artifacts use the pre-restart verified candidate export, later nightly artifacts the final verified export. Both archives and the host-side run identity, preflight and retirement receipts remain privately retained. The guest's later empty archive copy and rejected setup attempts were not used as acceptance proof. No profile database, configuration containing references to private services, credential input or SSH key is included. Helper logs contain technical state and only our public/synthetic content. Existing record content is preserved; this directory extends it.
