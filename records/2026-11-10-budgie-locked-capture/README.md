# Budgie: refuse screen reads behind gtklock

Part of put.gd-desktop #1383; code PR #1385. Confirmed on plain nightly7fc609dc42f8f3c1118d79a63d42ce37ea4a71c9: an agent desktop request made under visible gtklock completes and saves the lock screen. Fresh d69 KVM guests on the wall used Budgie10.10.3, labwc0.20.2 and gtklock4.0.0.

![Actual nightly capture versus final native-package refusal, annotated by its production editor](final/accept/c-before-after.png)

The adapter now requires a fresh compositor frame on its transparent, input-empty1x1 overlay before reading screen pixels. Real gtklock suppresses that frame. Setup has a bounded5-second deadline, then the actual frame witness gets its own1-second deadline. Close/error/silence fails closed with session_locked. Desktop and window pixel reads use this asynchronous gate; clipboard is unchanged. A live-region request can remain in its selector until pixel acquisition; this protects the pixel-read boundary.

Final head4b7e01d2b61c1a982ff1db9a053de53fb1d98154 was accepted from exact CI AppImage26.1110.4459-dev+g401d87382795, workflow42760262530. CI's synthetic merge401d87382795ae49399e8552c5d713652243c49b has parents nightly5e38f08df8d4dec14bc3828ea73d7b3912e4947b and branch4b7. Its source tree03f2f3cde95cc4af4e1c39e4e8f7aada13e33b96 matches local git merge-tree exactly. The intervening nightly changes concern docs and nightly-check scheduling. Build, package/running binary hashes and reviewed-source.json record this identity; none was bypassed.

| Native final-package case | Result |
| --- | --- |
| First cold request after fresh install/start, without warming the probe | completed |
| Real gtklock visible, three immediate desktop requests |3/3 failed: session_locked,0items, no new files |
| After unlocking | completed |

The first cold result is preserved separately and was not repeated/overwritten. A subsequent independent probe script initially lacked its wire helper; after adding that dependency we resumed only the locked portion. harness-correction.json retains this failure and correction. after/ contains earlier head930 intermediate results; final/ is authoritative. before/repro/fixed-locked-operation.json is a prototype result, not final acceptance.

The earlier implementation's whole-probe1-second timeout falsely refused the first unlocked request in three fresh guests. The bc4 trace shows0.906s spent waiting for registry setup, then destruction at deadline before configure. See startup-investigation for the actual trace and failed requests. This is why setup and frame deadlines are separate now; the first-window render was concurrent, but compositor internals were not profiled. The final fresh guest's first request passes. Earlier head930 also passed ten later unlocked repeats; those are supplementary, not final-head cold proof.

Lock routes checked on nightly: logind LockedHint remains no; BudgieScreenlock has Lock/Dim/Undim/OnBattery/ScreenPowerResume/ScreenPowerSuspend but no lock-state method, and GetAll is empty. gtklock exposes anonymous GTK application/window bus objects but no useful well-known state service; another anonymous connection's introspection timed out. We do not claim every possible logind signal route is absent. The useful observed signal is a fresh layer frame: the included minimal raw Wayland probe receives configure/sync in both states, but its frame only unlocked.

Plain nightly has no delayed capture yet. In the capture lane branch, lockGate bypasses zero delay and checks screensaver/logind for positive delay; its decisive gtklock refusal is the countdown pill's separate presentation/frame witness. The immediate adapter lacked such a witness. This fix uses the tested session-lock effect on layer surfaces; it is not a universal logind lock-state query.

Tests on f44 (Qt6.11.2, labwc0.9.6): the strict lockedDesktopCaptureIsRefused fails with the original adapter and passes fixed, including unlocked capture after unlock. Its fixture presents opaque lock surfaces on all outputs to match real gtklock; an empty lock object was insufficient on older labwc and was replaced without relaxing the assertion. A second regression pauses only the private child compositor for1.2seconds during setup: old deadline fails, new passes. Final full budgie_labwc_integration passes19.64s with all owned/component source paths matching head4b7. Earlier results18.78s differed only in the error text/header comment; those are retained. Ubuntu26.04 CI runs this real-labwc suite as well.

Picture: actual nightly saved lock-screen PNG left, actual final guest's locked QMP witness right, beside real operation results. Composition on d69; labels/arrow through the exact-package production editor after unlocking. No protected input shown. Raw selected lock-screen/QMP pictures, all operation receipts, scripts and failed experiments are retained; private archives have matching builder/workstation SHA256 and restore paths. All guests stopped and overlays guarded-retired after export; receipts included. Goldens unchanged.

No physical desktop, unrelated desktop acceptance, upload, workstation build or workstation test was run. No source docs changed.
