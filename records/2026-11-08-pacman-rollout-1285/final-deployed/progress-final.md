# #1285 signed pacman repository rollout

2026-11-08 03:17 UTC: Worker started. Read AGENTS.md, binding coordination, issue #1285, repository/release procedures, Arch implementation and worker E report, and SSH/audit memory notes. Shared main checkout remains untouched; private read clone at work/desktop-expansion-1275/rollout1285/source (origin/nightly 598de46c7 at inspection). No build or GUI work.

Step 1 WAITING: newest published release v26.1105.3986-nightly (published 2026-11-06T05:56:20Z); no qualifying Arch release yet. Scheduled cut 2026-11-08 05:23 UTC. No dispatch requested or performed.

Read-only d69 preflight: signer checkout clean, branch nightly, old SHA 1887c4c9a90dfd0d0bc37ef031757aab56bc04f7. Service inactive after successful timer run (published=[]); timer enabled/active, every ten minutes. zstd /usr/bin/zstd present. Live nightly v26.1105.3986-nightly; live stable v26.1105.3906; lab empty; no staged stable. Load 7.35, 96 GiB free home. Keys/config/units untouched, no host processes stopped. No desktop lock needed for SSH inspection/container testing.

Steps 2–6 NOT STARTED pending qualifying nightly. Stable signing explicitly excluded; next stable promotion uses sign_stable.py on workstation.

2026-11-08T03:17:17Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08 03:20 UTC: Additional prerequisite found: https://github.com/patrick-hudson/put.gd-site/issues/24 is still OPEN. Published https://app.put.gd/install SHA256 10c9988ea06a216a9bb1ccf0ffec92bf3cea30565847b519fc32d0a40fbce064 contains no archlinux/pacman support; current nightly source installer SHA256 01863698815a510fcad6a5ddceb290abece99bbf86b8b9bfc70da6021be15644 does. Coordinator: step 5 requires site #24 deployment (published installer + Arch permalink). No site modification authorized in this worker brief; will recheck after nightly. This does not prevent signer rehearsal/CDN validation.

2026-11-08T03:20:18Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08T03:23:19Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08T03:26:21Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08T03:29:22Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08T03:32:23Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08T03:35:24Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08T03:38:25Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08T03:41:26Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08T03:44:27Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08T03:47:28Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08T03:50:30Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08T03:53:31Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08T03:56:32Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08T03:59:33Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08T04:02:35Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08T04:05:36Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08T04:08:37Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08T04:11:38Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08T04:14:39Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08T04:17:40Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08T04:20:41Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08T04:23:42Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08T04:26:44Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08T04:29:45Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08 04:31 UTC: Coordinator steering acknowledged: if step 5 boots an Omarchy overlay, follow coordination rule 14 and docs/lab/remote-vm-displays.md immediately after launch: inspect free workstation ports starting at 5994, systemd-run SSH tunnel, back up and atomically update tools/qemu-grid/remote-displays.json with own tile, preserve others; remove own tile and stop own unit on retirement. Nightly wait remains active; no VM launched.

2026-11-08T04:32:46Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08T04:35:47Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08T04:38:48Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08T04:41:49Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08T04:44:51Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08 04:48 UTC: Saved public pre-rollout apt Release/InRelease/Release.gpg for all three distro labels and dnf repomd.xml on d69 at ~/work/rollout1285/baseline. Detached apt signatures all verified with the shipped nightly public key (command advanced through all three suites to repomd fetch). Also recorded old signer SHA, inactive successful service state, timer state, and configuration/unit SHA256 fingerprints without printing configuration contents. Source/config/units remain unchanged. f44 capacity preflight earlier passed (load 0.08, ~10 GiB available, 663 GiB free, Arch base image present, no running containers).

2026-11-08T04:47:52Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08T04:50:53Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08T04:53:54Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08T04:56:55Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08T04:59:56Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08T05:02:58Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08T05:05:59Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08T05:09:00Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08T05:12:01Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08 05:12 UTC: Coordinator/Patrick changed tonight's schedule: nightly.yml disabled at 05:11 UTC; workstation timer putgd-nightly-delayed-20261108 will re-enable and dispatch nightly at 07:23 UTC, expected Arch release 07:35–08:00 UTC. Continue waiting, do not enable/dispatch workflow ourselves. Signer still untouched, timer not paused; maintenance hold deferred until near delayed cut. No VM/container/lease active. Waiter continues checks every three minutes with real sleeps; disabled workflow itself is not a failed/skipped run.

2026-11-08T05:15:02Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08T05:18:03Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08T05:21:04Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08T05:22:52Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08 05:23 UTC: Waiter adjusted to delayed cut (07:23 UTC). gh run list by workflow name hides disabled workflows; preserved those errors in nightly-wait.jsonl, verified numeric workflow ID 382659607 with --all returns historical runs, and restarted only own waiter after exact-PID termination (1500230). No nightly run failed; no workflow enabled/dispatched. Replacement session 60026 polls every three minutes. Signer remains unchanged.

2026-11-08T05:25:53Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08T05:28:55Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08T05:31:56Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08T05:34:57Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08T05:37:59Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08T05:41:00Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08T05:44:02Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08T05:47:04Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08T05:50:05Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08T05:53:06Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08T05:56:07Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08T05:59:09Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08T06:02:10Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08T06:05:11Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08T06:08:12Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08T06:11:13Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08T06:14:14Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08T06:17:15Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08T06:20:17Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08T06:23:18Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08T06:26:19Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08 06:29 UTC: Site progress: published https://app.put.gd/install now SHA256 01863698815a510fcad6a5ddceb290abece99bbf86b8b9bfc70da6021be15644, exactly matching the current Arch-capable source installer. Original published bytes preserved in rollout1285/published-install.sh; refreshed in published-install-0628.sh. Site #24 still open but script-content blocker removed. Verify Arch download permalink when qualifying release arrives. Signer unchanged; delayed release gate remains pending.

2026-11-08T06:29:20Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08T06:32:21Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08T06:35:22Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08T06:38:23Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08T06:41:24Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08T06:44:25Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08T06:47:27Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08T06:50:28Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08T06:53:29Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08T06:56:30Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08T06:59:31Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08T07:02:32Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08T07:05:33Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08T07:08:34Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08T07:11:35Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08T07:14:36Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08 07:15 UTC: Rechecked d69 signer: service inactive/dead, MainPID=0, last status=0; checkout still clean at old SHA. Temporarily stopped only putgd-signer.timer to prevent an old-code automatic publication before rehearsal. Timer remains enabled (unit/config unchanged), now inactive; service checked inactive again after stop. Timestamp retained on d69 baseline/timer-paused-at.txt. Restore timer after successful publication, or on the prescribed stop/rollback path. No lab leases held before 07:15 UTC nightly-desktop boundary. Workflow untouched.

2026-11-08T07:17:37Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08T07:20:38Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08T07:23:39Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08T07:26:40Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08T07:29:41Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08 07:30 UTC: Coordinator's delayed run started 07:23:02 UTC: https://github.com/patrick-hudson/put.gd-desktop/actions/runs/42458568357. Plan/stable-scan/contracts/sanitizers and all four DEB/RPM package jobs passed; remaining Linux/Arch/AppImage work in progress. No qualifying published asset yet. Old signer timer held inactive, checkout unchanged. Worker has not enabled/dispatched any workflow.

2026-11-08T07:32:42Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08T07:35:43Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08T07:38:45Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08T07:41:46Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08T07:44:47Z: Step 1 waiting; release/run check saved in rollout1285/nightly-wait.jsonl. Signer unchanged.

2026-11-08 07:50 UTC: Step 1 PASS: https://github.com/patrick-hudson/put.gd-desktop/releases/tag/v26.1108.4139-nightly published 07:46:12 UTC, run 42458568357 SUCCESS. Arch asset 129275823 bytes, GitHub digest d38a612ea96e5b87c0bd1c6cf69f0ccc75f5aaac193f84f1206f353947336337.

Step 2 PASS: d69 clean nightly checkout fast-forwarded using fetch origin nightly + merge --ff-only origin/nightly, old 1887c4c9a90dfd0d0bc37ef031757aab56bc04f7 -> new 0eaff434d3530d3e09dc1663751eee960b7afa46. Config and both unit SHA256 values unchanged; zstd 1.5.7 present. Service idle/timer paused before update, state still carries previous live release and empty lab. No stable operation or workstation key access.

Step 3 running: ~/work/rollout1285/rehearse.sh on d69 independently verifies the complete published release, stages only the five native packages and their SHA256SUMS for publish-local under lab (AppImage excluded from lab rehearsal; its live-target zsync must not be relabeled as lab). All original release inputs retained in verified-release; lab-assets uses hardlinks to unchanged native payloads. Logs rehearsal.log/rehearsal.exit on d69; no blind retries.

2026-11-08 07:54 UTC: Step 3 local signature inspection PASS: gpg --verify reports GOODSIG + VALIDSIG 4032E28D893BAF66F4AC23D9A11D38D55536B371 for lab putgd-nightly.db.sig and exact Arch payload .sig; saved lab-signatures.log. Lab publication still in progress: exact started Python PID 1103486 has active S3 TLS socket with bytes_acked ~53 MiB after four minutes (~2 Mbps uplink), no failure/receipt yet. Do not duplicate/retry. First upload is still underway; live paths untouched. Native lab artifacts total ~640 MB (normal package publication, no VM/image upload).

f44 clean container rollout1285-arch prepared from official archlinux:base (identity in ~/work/rollout1285/image.txt); only this disposable container upgraded via pacman, with sudo/curl and initialized Arch keys. Saved original pacman.conf; removed container NoExtract restriction for complete payload as CI smoke requires. Published installer downloaded unchanged (01863698815a510fcad6a5ddceb290abece99bbf86b8b9bfc70da6021be15644). Socket preflight /tmp/p1285/r/putgd/session.sock = 31 UTF-8 bytes, PASS <=107. No app launched and no GUI claim.

2026-11-08 08:06 UTC: Lab publication PASS, rehearsal.exit=0, receipt ~/.local/state/putgd-signer/receipts/lab/v26.1108.4139-nightly.json result published/error null. CDN pacman db/package signatures+hashes and all apt checks passed in independent checker; checker first attempt stopped on its own missing zstd decompression for dnf primary.xml.zst (metadata checksum itself passed). Preserved cdn-lab-attempt1.log/.exit, corrected the checker to decompress .zst using installed zstd, and reran read-only verification; no publication retried and live untouched.

Coordinator prerequisite: https://app.put.gd/dl/nightly/archlinux still HTTP 404 at 08:05 UTC (release published 07:46). Published installer now supports Arch but its availability preflight will fail until site #24's KVS/permalink update is deployed. This blocks requested published-path installation; signer rollout can still proceed after full lab readback.

2026-11-08 08:07 UTC: Step 3 PASS: corrected independent CDN verifier exited 0 for lab, including pacman db/package detached signatures against pinned nightly fingerprint, hash equality to independently verified GitHub SHA256SUMS, signed checksums, all apt Release/InRelease/Packages signatures+hashes+version, all dnf repomd data hashes/current version and signed RPM receipt mapping/verification. cdn-lab.log + downloaded public artifacts retained on d69. First checker error was .zst handling only; no signer retry.

Step 4 STARTED: normal systemd user putgd-signer.service invoked once via systemctl start --no-block after confirming idle and lab verification=0. Timer stays paused to avoid automatic retry. Invocation and start time retained in live-invocation.txt/live-started-at.txt. Monitor for failure and preserve journal/receipt; roll checkout back immediately if apt/dnf affected.

2026-11-08 08:23 UTC: Step 4 PASS: normal signer service exited 0, live nightly publishedAt 08:21:51 UTC. Independent CDN verifier cdn-live.exit=0: db + package detached signatures verify with nightly fingerprint; db SHA256 and exact package bytes equal independently verified GitHub SHA256SUMS (Arch d38a612ea96e5b87c0bd1c6cf69f0ccc75f5aaac193f84f1206f353947336337). Signed SHA256SUMS verified with nightly minisign public key. All three apt Release.gpg/InRelease verified, clearsigned bodies match Release, Packages hashes match signed Release and contain this nightly's release hashes. All dnf repomd data checksums passed/current package version confirmed; signed RPM fetched from CDN, receipt maps GitHub original hash to repository signed hash, RPM signature verified against nightly key. No apt/dnf regression or rollback needed. Live receipt https://pkg.put.gd/receipts/v26.1108.4139-nightly.json, SHA256 6fcac8053d10b904670665b7aca947eec46473deb86e319298f7ec1699553a8f. Stable remains v26.1105.3906, no stable stage. Config/units SHA256 unchanged; signer timer restored active/enabled after readback passed. Live journal + monitor JSON retained.

Pacman live URLs: https://pkg.put.gd/pacman/x86_64/nightly/putgd-nightly.db and .sig; https://pkg.put.gd/pacman/x86_64/nightly/putgd-26.1108.4139-nightly-archlinux-x86_64.pkg.tar.zst and .sig. Public response artifacts and verifier output retained under d69 ~/work/rollout1285/cdn-live and cdn-live.log.

2026-11-08 08:23 UTC: Step 5 published installer FAIL/BLOCKED: exact published script in clean f44 container exits 1 with `put.gd: No usable nightly archlinux download (HTTP 404)`; pacman confirms putgd absent. This precedes any repository/key configuration. Logs published-install-attempt1.log/.exit on f44. Cannot close #1285 as fully passed while site #24 permalink remains absent. Running a separate direct-CDN repository test with the same pinned-key/repository setup and PackageRequired DatabaseRequired to establish whether pacman installation/version/uninstall work; this is explicitly not a pass for the published installer. Optional Omarchy run deferred because the same published-path prerequisite is missing; no VM launched, so no wall tile/tunnel needed.

2026-11-08 08:25 UTC: Step 5 direct-repository check PASS (published installer path remains FAIL): clean official Arch container on f44 fetched the nightly public key, checked its full fingerprint, added/locally signed it, wrote /etc/pacman.d/putgd.conf with SigLevel PackageRequired DatabaseRequired and included it from pacman.conf. `pacman -Syu --noconfirm putgd` installed from pkg.put.gd; `pacman -Qkk putgd` passed; `putgd-cli --version` matched 26.1108.4139-nightly; `pacman -R --noconfirm putgd` passed and package/binary absent afterward. Admin repository configuration remained as designed. This was direct setup, not an edited installer or a substituted download; original published-path HTTP404 failure remains preserved. f44 evidence direct-install.log/.exit, installed-version.txt, putgd.conf, pacman.log, container-inspect.json/image.txt; direct-install.exit=0. Exact owned container ID checked before stop/remove, receipt container-retirement.txt; shared base image and other workloads preserved. No GUI/VM/desktop acceptance claim.

Optional Omarchy overlay NOT RUN because the published installer availability prerequisite is unresolved; no VM, workstation tunnel or wall tile was created. Stable signing NOT RUN by design: next stable promotion uses sign_stable.py on the workstation; stable key never touched. Steps 1–4 passed; step 5 published path failed, independent direct repository installation passed; step 6 will post results and keep #1285 open for site #24 / installer recheck.

2026-11-08 08:27 UTC: Step 6 PASS for reporting: results posted https://github.com/patrick-hudson/put.gd-desktop/issues/1285#issuecomment-6719251234 ; issue intentionally left OPEN because published installer prerequisite still fails HTTP404. No code or docs PR needed/created. Stable-key operation excluded as requested.

Cleanup confirmed: f44 exact owned container d5b7a3dac4252d06442a9cb5d35a4503d6634aadbfc3754df9245a2f2401eb96 removed 08:25:26 UTC after logs/config/version/inspection export. Its sleep-infinity PID1 did not terminate within podman's 10-second grace; podman used SIGKILL only in that owned container. No containers remain running from this worker; base image retained. d69 own public-verification gpg-agent PIDs 1103759, 1104795, 1106096 stopped only after checking uid, comm and owned ~/work/rollout1285 homedir; receipt verification-agent-cleanup.json. Production signer agent untouched. Local waiter and live monitor completed. Corrected live journal collected by unit and precise start time (invocation-field query initially returned no entries); confirms one successful publication and a subsequent successful empty timer run. Exported small public evidence to rollout1285/evidence-{d69,f44}; large public package inputs retained only on builders. No VM overlays, leases, workstation tunnel/wall edits or EC2 resources to retire.

Final outcomes: 1 PASS; 2 PASS; 3 PASS; 4 PASS; 5 FAIL published installer (site #24 HTTP404), PASS separate direct repository install/version/uninstall; optional Omarchy NOT RUN. 6 PASS comment, closure withheld until installer passes. Next stable signing remains the next stable promotion's workstation sign_stable.py operation.

2026-11-08 08:49 UTC: Coordinator resumed step 5 after site #25 deployment. Fresh official Arch container ran real `curl -fsSL https://app.put.gd/install | sh -s -- --channel nightly` interactively: PASS install/key/repo/signatures/version 26.1108.4139-nightly, Qkk and uninstall. Omarchy fresh overlay o1 (run 03045c55-7b1a-451b-a094-753411ef9e17, f44 QEMU2857738, SSH22443/VNC5943/wall5997) showed unlocked Hyprland on wall, then published installer FAILED with Omarchy's intentional direct `pacman -Syu` guard. Also found new putgd.conf mode0600 from inherited umask077, preventing non-root pacman reads. Auth-only attempt canceled at masked sudo prompt; subsequent attempt supplied protected local login input in memory with no echoed/logged value. No package installed on Omarchy; no acceptance claim. Failed visual and logs exported+checksum-verified, overlay guarded-retired (bb118b0085e79daacd14789cca983b7aa2f8f177213e158a5b199f577a5a3c66 manifest); wall entry/tunnel removed, container retired. Golden and other workers untouched.

Fix PR https://github.com/patrick-hudson/put.gd-desktop/pull/1310 head 6f746f7b371163c232b9db8730ff3a13e197aece. Coordinator selected native updater: command-based detection, explicit /dev/tty confirmation then omarchy-update -y before any repo/key changes; failure/decline/noTTY stops; after successful system update refresh only new put.gd repo and install with -S; other Arch stays -Syu. No Omarchy bypass variable. Root public config created mode0644. 25 installer tests PASS on f44, including piped stdin + controlling tty, failure/noTTY/decline preservation, command-based detection and permissions. Real pacman accepts repository-only sync command. CI currently in progress, 0 review threads at inspection; no merge authorized to worker. Watch tool attempted but unavailable (not callable). Preparing real candidate check before requesting merge; deployed-script retests remain pending. No new issues.

2026-11-08 08:53 UTC: PR1310 marked ready for review, CI + automatic reviewers running; zero threads at last inspection (not final). Shell syntax and shellcheck warning-level checks PASS. Fresh candidate overlay o2 (d527339c-b489-4b36-91e9-61b47ee14623, f44 QEMU2864328) registered immediately with unit putgd-vm-1285-o2 and wall5997; unlocked Hyprland preflight/visual saved. Candidate failed before updater/configuration because GitHub's exact SHA256SUMS release-download URL returns HTTP504, reproduced from workstation and f44; pkg.put.gd mirror returns200. No inputs substituted; candidate log/exit and host probes preserved. Exported verified evidence, guarded-retired o2 (manifest 06db664d414b1246a4b16b2e35d51c75f06f2f4e84c4e4024550aeb27a755fcb), removed only its wall entry/tunnel, closed own wall preview tab. All own VMs/containers retired; fresh deployed-script tests remain required after coordinator merges PR1310 and site deploys it. No issue filed. Shared main checkout branch/source unchanged.

2026-11-08 09:00 UTC handoff state: PR1310 head e32d98f63f40eab0044e6bedce1dcb57878e2de3, ready for review, not merged. Permission-migration review fixed/replied/resolved; 0 unresolved threads at last inspection, fresh automatic review still running. Final f44 suite 26/26 PASS (installer-tests-final.log), syntax and warning-level shellcheck pass. CI for this head is IN PROGRESS, not green/accepted; do not merge until required CI summary succeeds and reviews settle with zero unresolved threads. PR watcher capability is absent in this session (attempted callable name, TypeError, no tool metadata entry), so no automatic PR watch registered. Coordinator must resume this worker for any review/CI fixes and after merge/site deployment for both real published-path reruns, native Hyprland start, uninstall, retirement and #1285 closure. Pending gates remain pending, not left as accepted.

Pinned sanitized evidence published via evidence.py: https://github.com/patrick-hudson/put.gd-evidence/tree/fa7a1ae48aaf9e8beddf46cc731dc54c734d638a/records/2026-11-08-pacman-rollout-1285 (original d3066d5 plus add-only final validation/test log). The protected default's text is also a generic public lab-service/file prefix; a byte-substring audit flagged only those pre-existing public names, not any revealed credential. Protected input/private keys excluded. Own VM PIDs2857738/2864328 absent, both disks retired, 22443/5943 free, no own running containers; 5997 entries/tunnels removed, other tiles preserved. Issue progress comment https://github.com/patrick-hudson/put.gd-desktop/issues/1285#issuecomment-6719536749 . No new issues. Current step outcomes: container published path PASS; Omarchy published path FAIL fixed in unmerged PR, runtime startup and final deployed retests PENDING; closure PENDING. Live signer/repositories remain PASS.

2026-11-08 09:43 UTC: Final deployed script fetched SHA256 93ebb6589c64e95724970680e564e5065538851105322c186c1baaeb2ce9dbd9 after coordinator merged #1310 fa81f53f1/site deploy. Real fresh-container and Omarchy no-TTY paths both still fail upstream GitHub SHA256SUMS with HTTP504 before intended checks. Preserved failure logs and raw error/selected headers; direct release URL returns504 with curl and signer UA, both workstation and f44; public pacman CDN db returns200. This is a redundant dependency: Arch first downloaded unsigned-release SHA+payload via GitHub, then pacman downloaded and signature-verified it again. Preparing focused fix on own branch fix/1285-pacman-installer-repo-only from origin/nightly fa81f53f1: Arch delegates index/payload download to mandatory database/package signature validation using pinned channel key; other formats retain their SHA256SUMS checks. Availability preflight remains. 27 tests PASS on f44, shell syntax and warning-level shellcheck PASS.

Fresh o3 overlay (f44 SSH22443/VNC5943, wall5997/unit putgd-vm-1285-o3) remains visible/unlocked. Candidate noTTY now gives prescribed recovery message; candidate declined prompt leaves no package, no putgd.conf and no Include. Candidate accepted prompt has entered real native Omarchy update (not bypassed) and is running snapshots/upgrades/migrations. These are candidate checks, not deployed-script acceptance. Container candidate installation in progress from real signed repository. No new issues, signer/stable keys untouched.

2026-11-08 09:49 UTC: PR1311 head 9dfa3c70c3ce7f9d3f0a9b76491fe814959f5081 opened (no merge). Candidate all requested checks PASS: container signed-repo install/version223files0altered/config0644/uninstall; Omarchy noTTY clear recovery+decline no package/repo/Include, accepted full native updater (snapshot/keyrings/upgrades/migrations/hooks/boot checks), correct repo package/version, native Hyprland GUI visible on wall and saved frame, capabilities/diagnostics, ui.quit successful socket/process disappearance, uninstall. Helper-only mistakes preserved: hyprctl version returned4 before launch; then lab.guest_session string-return was treated as CompletedProcess after successful launch; corrected readback collected without relaunch. No package/app failure. Scope is candidate, not yet deployed script. Published-script checks remain blocked by exact GitHub checksum HTTP504 until coordinator merges/site deploys this fix; user requested PR rather than worker merge.

Evidence: https://github.com/patrick-hudson/put.gd-evidence/tree/4a98479231b8ee0b063a7054395b45f46b156663/records/2026-11-08-pacman-rollout-1285/pr1311-candidate ; add-only record, original failures retained. o3 run9284e132-e959-494a-be01-fd5610b418d4/QEMU2869110, golden SHA bd74b7832c4a43f15a06f5a5b448e670a77d33ae75516b5bc5856773b69f3256. Completion manifest9f059f89132e6a21bdddedf172496cd4364556d98391ecc1e5a57147cae5141c; guarded retirement complete09:45:30 UTC. Container retired, both guest ports22443/5943 free, PID/disk absent, only owned wall5997 entry/unit removed, own preview tab closed. No physical leases/resources left, no new issues. CI/reviews in progress, 0 open threads at inspection; no final green claim. Resume after merge/site deploy for final fresh deployed paths and #1285 closure.

2026-11-08 11:22 UTC: Final deployed-only verification resumed after coordinator merged #1311 a7554a4a8 and redeployed site. Downloaded install.sh SHA256 0989850208e7689885b7a474d28fe51553f4f4d9d86a268d2f6729c00b611286; Git blob ff29bc846557e782e94204781043e369405ee930 exactly equals a7554a4a8:packaging/install.sh. Fresh official Arch container rollout1285-deployed and new f44 Omarchy o4 started with capacity/KVM/port checks, private socket paths50/50/31 bytes PASS. o4 on wall5997/unit putgd-vm-1285-o4 immediately from launch; other tiles preserved. Initial guest SSH connected before fresh-key bootstrap finished (authentication-only failure, no protected input sent); own waiting SSH PID1777796 stopped, failed attempts retained and commands repeated only after successful launch preflight. Deployed noTTY and declined prompt now PASS with no package/config/Include; accepted real curl|sh in real TTY now running full native Omarchy updater, no override. Fresh container deployed install also in progress. No source edits/candidate substitution.

2026-11-08 11:24 UTC FINAL DEPLOYED ACCEPTANCE: Steps 1 and 2 PASS with unmodified live `curl -fsSL https://app.put.gd/install | sh -s -- --channel nightly`, no candidate substitution. Script SHA256 0989850208e7689885b7a474d28fe51553f4f4d9d86a268d2f6729c00b611286 matches merged a7554a4a8d8b837f2473ed59802e8a9b1049857c Git blob ff29bc846557e782e94204781043e369405ee930. Guest re-download after installation has same SHA. Fresh official archlinux container on f44: mandatory db/package signature repo configured, nightly key fingerprint4032E28D893BAF66F4AC23D9A11D38D55536B371 trusted; version26.1108.4139-nightly, pacman-Qkk223files/0altered, config0644, uninstall/package+binaryabsence PASS. Fresh Omarchy o4: noTTY exits1 with explicit Run omarchy update/terminal guidance; declined terminal prompt exits1 with no installed package/repo config/Include. Accepted prompt completes full actual native updater then syncs put.gd repo and installs through -S, no direct-pacman override or preparatory -Sy. Native production GUI visibly running in real Hyprland/QtWayland on wall5997, exactversion/Qkk223zeroaltered, capabilities/diagnostics and ui.quit PASS; socket/process gone; uninstall PASS, admin repo config remains readable as designed. This is installation/startup acceptance, not a broader capture/recording certification of unmerged Hyprland support.

o4 identity: 7aa34550-9bbf-443c-8a8f-8e0534ad9904/QEMU2875050 on f44; immutable golden bd74b7832c4a43f15a06f5a5b448e670a77d33ae75516b5bc5856773b69f3256, KVM/2CPU/6144MiB/UEFI/virtio-vga, SSH22443/VNC5943, own wall5997/unit putgd-vm-1285-o4. Saved native-startup-head0.ppm SHA5a3596b708a4f18f2d80b29c96c2792628dbf14a79fa4092ad5760cc81c7f349 and after-uninstall-head0.ppm SHAd22e9aeedae0582b6f4b66e95b88254e0a3485cf6c6c0196511153e1a3f574bb. Complete evidence exported and independently checksum-verified before guarded retirement. Cleanup manifest ebc088f50a709bc4bc440052a040f4b64ced4a6564277cf4b9e7577e17bd8ac3, completed11:23:32 UTC. Own PID/disk/containers absent, guest ports22443/5943 free; removed only owned wall entry and stopped tunnel; own browser tab closed. Golden, other sessions and Patrick's processes untouched. No new code changes/issues/PRs. Final acceptance evidence publication and #1285 closure follow.
