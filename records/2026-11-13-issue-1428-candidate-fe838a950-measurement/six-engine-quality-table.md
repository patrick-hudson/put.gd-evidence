Candidate **fe838a950**, dispatched **run43394391197**: complete178-image helper quality on all six engine builds, corrected174 +two4K +two24px pages. No classes or engine builds pooled.

| Class / size (CER bar) | Mint22 / Ubuntu24 | Ubuntu26 | Debian13 | Fedora44 | Arch23MB | AppImage5.5.4 |
|---|---:|---:|---:|---:|---:|---:|
| browser-github/body>=11px (2%) | 0.147% | 0.147% | 0.147% | 0.147% | 0.147% | 0.147% |
| browser-local/body>=11px (2%) | 0.000% | 0.000% | 0.000% | 0.000% | 0.000% | 0.000% |
| browser-wikipedia/body>=11px (2%) | 1.874% | 1.874% | 1.874% | 1.874% | 1.533% | 1.874% |
| editor-code/body>=11px (2%) | 1.650% | 1.758% | 1.758% | 1.619% | 1.441% | 1.617% |
| monitor/body>=11px (2%) | 0.000% | 0.000% | 0.000% | 0.000% | 0.000% | 0.000% |
| small-ui/body>=11px (2%) | 0.421% | 0.443% | 0.443% | 0.417% | 0.088% | 0.399% |
| small-ui/small<11px (5%) | 0.089% | 0.089% | 0.089% | 0.067% | 0.067% | 0.067% |
| synthetic-24px/body>=11px (2%) | 0.000% | 0.000% | 0.000% | 0.000% | 0.000% | 0.000% |
| terminal/body>=11px (2%) | 0.000% | 0.000% | 0.000% | 0.000% | 0.131% | 0.000% |

| Engine | URLs exact | Email exact |
|---|---:|---:|
| mint | 52/52 (100.00%) | 52/52 (100.00%) |
| ubuntu26 | 52/52 (100.00%) | 52/52 (100.00%) |
| debian | 52/52 (100.00%) | 52/52 (100.00%) |
| fedora44 | 52/52 (100.00%) | 52/52 (100.00%) |
| arch | 50/52 (96.15%) | 52/52 (100.00%) |
| appimage | 52/52 (100.00%) | 52/52 (100.00%) |

All listed class medians and exact-entity rates meet their quality bars. The two mixed4K images are only2/26 monitor cases; that median must not hide their individual errors. Their CER values by engine:

- mint: gnome4k-monitor-light 9.242%, gnome4k-monitor-dark 9.302%
- ubuntu26: gnome4k-monitor-light 9.242%, gnome4k-monitor-dark 9.271%
- debian: gnome4k-monitor-light 9.242%, gnome4k-monitor-dark 9.271%
- fedora44: gnome4k-monitor-light 9.293%, gnome4k-monitor-dark 9.230%
- arch: gnome4k-monitor-light 9.118%, gnome4k-monitor-dark 9.343%
- appimage: gnome4k-monitor-light 9.200%, gnome4k-monitor-dark 9.188%

Arch’s helper-memory report is being checked with a post-exec kernel observer: RUSAGE_CHILDREN may include pre-exec inherited memory. Do not treat that field alone as a settled helper-memory verdict. Quality figures above remain complete; timing/gateC/privacy/clipboard/editor/codes are separate pending measurements.

German on the dispatched Mint/Ubuntu24 helper with distribution deu data: 12 captures, 816 reference words, medianCER 0.000% (2% bar met). Data hashes retained.

Kernel post-exec peak verification confirms **Arch English141.3MiB on a small real capture: MISSED128MiB**. For dense24MP, read candidate-kernel-peaks.json instead of RUSAGE_CHILDREN: the latter includes inherited pre-exec parent image memory and overstates native/AppImage peaks. All dense24MP jobs returned partial text with truncated=true inside their time budget.
