import pathlib,json,statistics
E=pathlib.Path('/home/patrick/work/putgd-evidence/2026-11-10-recording-1364-budgie-4548');c=json.load(open(E/'comparison.json'));m=json.load(open(E/'motion.json'));state=json.load(open(E/'identity/state.json'));rings=json.load(open(E/'ring-effect.json'));g=next(r for r in c['newRows']if r['tag']=='g-new-driver');d=g['delayedCaptures'];maxerr=max(max(abs(v['dx']),abs(v['dy']))for v in rings)
t=['| Build | Pointer / highlights | Four A/V medians / mean frame ages (ms), repetition order | Median range width ms |','|---|---|---|---:|']
for x in c['cells']:t.append(f"| {x['build']} | {x['mode']} / on | "+'; '.join(f'{v:g} / {a:g}'for v,a in zip(x['medians'],x['ageMeans']))+f" | {x['spread']:g} |")
(E/'summary-table.md').write_text('\n'.join(t)+'\n')
s=f'''# Budgie new-build report — 4548 / 30eab18a8

**Requested functional retests PASS:** monitor and region rings, cleanup immediately after Stop, and same-session delayed capture/recording/delayed capture. All eight parked/swept clips are retained and within the absolute A/V bound. The measured timing samples overlap; they do not establish a before/after improvement beyond the spread. Original large early offsets are not explained or waived.

Build under test: CI42784508070, source head30eab18a8fa9954438eaa48e9b417b177632b9fd, observed completed/success before testing; release-appimage version26.1110.4548-dev+gf65c1053b22d, CI merge/package commitf65c1053b22d1c7e3a5905945ff7dcc1401dc3b7, treec516a5106b716035bf76b717c7e1a104983450b0. AppImage SHA25606f27e641ce932e241151fd69040ae18214699bdbabb33933d03942caa160611. Actual resident logs confirm loaded Qt6.12.0 and this build version. CI was polled with a one-minute guard, not gh run watch.

Fresh d69-hosted guestb1364n, run{state['id']}, QEMU{state['pid']}, 2vCPUs/6144MiB, 1280×800, UID1000/lab, Budgie Wayland. Same immutable Fedora45 golden (Budgie10.10.3/labwc0.20.2), SHAa6749512438d507ef2b2c47fe675955627464d9a5a85341002f91cd54fb401ad; no guest OS package changes. Host192.168.68.69/d69, Debian13/four cores. Visible wall via workstation5996→d695946, SSH22446; saved desktop/frame visuals retained. This is a separate fresh guest from the current-build report, not a same-session binary A/B.

Protocol: parked/on, swept/on, repeated four times in strict alternating order. Region0,0,1280,400, lead3s, same private output for all eleven new-build cases, same byte-identical marker as build4538 (SHAabf5305fb0b9a1124ad1efc37af6b924484d0917955513060560360b2f6fb2ea). Sweep720px/s, x100…1180/y100, nominal60updates/s, starts before Record and lasts until Stop replies; parked stays(200,100), including clicks. Actual update counts/times retained. Both builds use the same input/marker parameters and the supported bar-hide method at Ready; original guards remain active. Each original and exported clip was copied before a guard could delete it. No new gate failed.

Driver provenance: copied the requested coordination file after NEW HEAD (SHA410d4093573743f088c5bfa9fd6ac14b114b43cbc575b3992f2636b3f58ff00e). It still differed from the pushed source only by the Hyprland delayed-capture fullscreen hold. Used the exact pushed tools/lab/record_run.py instead (SHAaa7fec68b7c69c78c6443ff5c89c8a564f1fe584e522c93b01917a9c823ca31a), with --hide-bar plus preservation/identity instrumentation (SHA421b2d4e6f70c35fa36d9c76c5d76b7a8e87872ec9bc96ab4705d8a5c26d5cc3). Both originals are retained. No product code, branch or PR edits; no compilation on the builder or workstation.

A/V values below are exported-clip medians; negative means sound earlier. Frame-age values are the **means** from the helper's min/mean/max Stop diagnostic. Full triples, sample counts, both raw Stop lines, cursor-only drop counters and every ordered marker pair are retained.

'''+ '\n'.join(t)+'\n\n'
s+='''Within-build paired swept-minus-parked differences, repetition order:

| Build | Four paired differences ms | Median paired difference ms | Difference of cell medians ms | Larger cell range width ms | Cell ranges overlap |
|---|---|---:|---:|---:|---|
'''
for v in c['contrasts']:s+=f"| {v['build']} | "+', '.join(str(n)for n in v['pairedSweepMinusStill'])+f" | {v['medianPairedDifference']} | {v['differenceOfCellMedians']} | {v['maxWithinCellRange']} | {v['rangesOverlap']} |\n"
s+='''
The paired median moves from−17.65 to−16.95ms (0.7ms toward zero); differences of cell medians move from−17.0 to−10.3ms. Both are much smaller than the observed cell spreads. Samples overlap within and across builds, and each build has a paired run with the opposite sign. This experiment does not resolve an improvement beyond run-to-run variation or establish a consistently early click-path defect. This is not a claim that the unit-tested frame-slot effect is absent. The fresh-guest baseline changes too, so raw before/after medians are not attributed to the fix. No DEFECT-headed STATUS line is added.

Every new motion clip has16 marker pairs and real motion (scores19.14…19.17), saved working/export clips and passing cover edges. Seven of eight meet the±33ms target; the65.3ms parked clip misses that target but meets−45…+125ms. The original−66/−118.7ms measurements remain in the first report, with frame-age mean2.5ms; no extra~100ms of captured-frame age was observed there. Their cause remains unresolved.

Functional retests (same new build):

| Case | Corrected ring delays ms | Maximum absolute centre error px | A/V median ms | Motion | Result |
|---|---|---:|---:|---:|---|
'''
for tag in ('f-monitor','f-region','g-new-driver'):
 rr=[r for r in rings if r['tag']==tag];row=next(r for r in c['newRows']if r['tag']==tag);err=max(max(abs(r['dx']),abs(r['dy']))for r in rr);s+=f"| {tag} | "+'/'.join(str(r['delayMs'])for r in rr)+f" | {err:g} | {row['medianMs']} | {row['motion']} | PASS; retained/full frame gate passed |\n"
s+=f'''
All9rings appear at the requested places and within−33…+34ms of the client's visible flash, maximum error{maxerr:g}px. Timing is not measured against pointer arrival. Monitor and region after-stop XML snapshots contain zero put.gd click markers and preserve all83 user keybindings structurally; all eleven cases have zero markers immediately after production Stop, before cancel/quit.

g uses one resident for desktop countdown→recording with highlights→desktop countdown. Both captures completed/saved in{d[0]['tookS']}/{d[1]['tookS']}s,6031 countdown pixels each, full cover gate passed; capture operation IDs{d[0]['operationId']} and{d[1]['operationId']}. BarHidden true; expected overlayExcluded false / overlayPlacement handle; the hidden handle is absent from the retained clip. All recording-frame edge scores1.0; rc.xml is byte-identical before/after. Driver exit0, no reported problems. The43.3ms g median misses the one-frame target while meeting the acceptance bound. Working/export clips, preservation copies, ring frames, countdown visuals and after-Stop snapshots are retained.

Guest load averages1/5/15min: {m['loadAtStart']} → {m['loadAtEnd']}; per-run start/end values retained. Host snapshots show only this guest, no builds/other VMs, alongside the existing owner desktop/VNC/sampler/ChatGPT and idle service/demo processes; owner's versitygw/smb untouched. Only private guest audio was used, defaults restored, modules removed (left[]). Every resolved recording socket is33UTF-8 bytes; launch checks QMP/VNC paths.

Export verification:208files, zero mismatches. Guest synced/stopped, guarded overlay retirement completed; golden preserved, tunnel stopped and exact wall tile removed. No physical desktop lease was used; no owned process remains on d69. Private host-side run/cleanup/plot metadata retained. Code worktree clean. This packet follows current-build evidence86f56d063719733fac9b966330f300f8a97446d0.

![Before and after](plots/comparison.png)

[Every pair trajectory](plots/ordered-pairs.svg)

## Every new run and pair

'''+(E/'ordered-pairs.md').read_text()
(E/'README.md').write_text(s)
