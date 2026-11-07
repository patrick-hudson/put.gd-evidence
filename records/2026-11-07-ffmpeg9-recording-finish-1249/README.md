# PR 1249 recording acceptance completion

Candidate: `putgd-26.1107.4046-dev+g8ed31be16488-x86_64.AppImage`, CI 42403829742, supplied for PR head `508970b5e76c6f0ff636594d8817db00cbbcd575`. Baseline: `putgd-26.1107.4036-dev+g369f001b66a9-x86_64.AppImage` (FFmpeg 7.1.5). Exact SHA-256 values and verified hosts are in tested-assets.json. Both assets matched on d69 and f44 before desktop work; no artifact downloads, package operations, code changes, branch changes or commits in the shared product checkout occurred.

Ubuntu 26.04.1 / GNOME 50.1 / native Wayland: fresh KVM overlay `178b5568-5cb6-420d-ad42-46b49bf6300c` on d69, immutable golden SHA-256 `563730cc1d929bd946d20cf30a9aecfe3c4ad40eb12ba7f9abcff1c461e342bb`. Visible on workstation wall port 5993 through a pinned SSH tunnel. GIF and WebP reran against the fixed candidate and nightly, interleaved, with a two-second pause. Every saved frame shows the synthetic moving bars. The overlay was exported, checksums verified, stopped and retired using guarded cleanup; its receipt is retained. d69 lock cleanup passed and was released. No golden or Patrick demo was changed.

The fresh guest filesystem had 33,632,829,440 total bytes and 3,306,418,176 available before staging. One extraction of each AppImage left 2,289,827,840 available. The default system reserve is total/20 = 1,681,641,472 bytes, plus the three 64 MiB admission budgets (201,326,592 bytes). Pre-run df records remain with each run. Scored exports and retained working clips were unlinked by their exact recorded names; their hashes remain in stable-motion.json. No recording hit a budget stop. Final available space was 2,285,555,712 bytes. This fresh disk was sufficient without expansion.

Methods: earlier round's record_run.py / cover_player.py with the earlier ximagesink variant, cached extracts, product CLI, real Mutter screencast and software x264. Each resident waited 11 seconds after readiness for startup recovery, and recording.overlay hid its controls through the product method. Fedora's full-screen cover precheck initially rejected the top strip (97.37% versus 98% required); the corrected precheck applies the unchanged 98% gate to the exact 1120x600 recording rectangle at 80,140. Capture remains native Wayland even though the synthetic cover uses X11. No saved export frame contained Settings. Initial failures are preserved in per-attempt results and harness logs.

Motion is mean absolute grayscale difference across eight decoded samples. Fedora uses 2 seconds through 150 ms before the end; Ubuntu moving uses 1 second through 150 ms before the end. Ubuntu's first short still controls included an opening transition in both builds; the longer repeated controls sample after 2 seconds and all score 0.000. Raw scores and sample timestamps remain in every record. Pillow decodes animated GIF/WebP; the exact helpers decode MP4/WebM. Ubuntu per-run export cleanup followed scoring, so only synthetic PNG frames leave the guest.

Ubuntu MP4/WebM, same-input A/V sync and History posters were already passed in the earlier round, and are reused as requested, rather than claimed as fresh fixed-build tests. That candidate was `26.1107.4044-dev+g33af4071b5fa`, SHA-256 `d59c2e68bd7bbf4d6864bab36a291dc3035adb145af9362c516296e78ccaa83b`. Earlier evidence: https://github.com/patrick-hudson/put.gd-evidence/tree/ed16f8ef904eec8be2babdbcc84ea556a6d4f2f7/records/2026-11-07-ffmpeg9-recording-1249. Selected original score and A/V JSON are copied under ubuntu-earlier for precise provenance.

Fedora 44 / GNOME 50.6 / native Wayland, physical f44: all four moving formats and still controls pass with software x264 capture. Pauses were 2 seconds in the format sweep and 3 seconds in the A/V sweep. Live A/V capture-step changes were +0.6/-0.2 ms for MP4 candidate/baseline and -0.3/-0.3 ms for WebM; export-minus-working changes were +1.0/-1.0 ms and +1.8/-0.2 ms respectively. Same-input exports by both builds agree exactly in every median (17 pairs per file):

| Working source SHA-256 | MP4 candidate / baseline ms | WebM candidate / baseline ms |
|---|---:|---:|
| `785fc0f9ceb18e9eb2793acdff1a7577ee936b5f937cc42275b8d98a6de61ad5` | 39.3 / 39.3 | 39.5 / 39.5 |
| `37a0bb7a3d7822bd65705c7b475604b786aca842734193614a56688e3af85930` | 21.3 / 21.3 | 21.5 / 21.5 |

| Desktop / format | Motion candidate / baseline | Still candidate / baseline | Pause/resume |
|---|---:|---:|---|
| Fedora GNOME / MP4 | 22.045 / 18.827 | 0.000 / 0.000 | PASS / PASS |
| Fedora GNOME / WEBM | 20.691 / 21.813 | 0.000 / 0.000 | PASS / PASS |
| Fedora GNOME / GIF | 19.720 / 19.045 | 0.000 / 0.000 | PASS / PASS |
| Fedora GNOME / WEBP | 20.759 / 20.268 | 0.000 / 0.000 | PASS / PASS |
| Ubuntu GNOME / GIF | 25.619 / 25.848 | 0.000 / 0.000 | PASS / PASS |
| Ubuntu GNOME / WEBP | 25.820 / 25.587 | 0.000 / 0.000 | PASS / PASS |

Fedora History passed for both builds: the explicit upload completed into the private local archive, history.preview returned ready for exact history IDs, and the inspector selected each row. These local-only acceptance operations used no remote destination or user object. Synthetic poster PNGs are under f44/history/frames. All eight format-sweep frames and four Ubuntu frames were inspected visually and show only the owned magenta cover and scrolling bars; no Settings window appears. Both physical desktop locks passed cleanup and were released; receipts are included. The only Ubuntu host scratch disk (1,180,123,136 allocated bytes) was retired; all evidence, parameters and failure context remain. The wall's owned VM tile and SSH tunnel were removed. Existing desktop work, demos and the shared checkout were preserved.

Outcome: the two requested rows pass. No candidate-only failure was found. Initial harness blockers (coverage strip, missing gtksink, and an opening transition in short controls) affect baseline as well; their failed attempts and corrections are retained. Ubuntu MP4/WebM/A/V/poster acceptance is explicitly reused from the previous round, as requested. Other PR checklist gates are outside this completion report.
