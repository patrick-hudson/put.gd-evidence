# Final CI and merge readiness

The approved tree implementation and its two updated catalog references are at
`5f469b332550a7ea422c12fc1c587c36bd1fdc70` in
[code PR #1253](https://github.com/patrick-hudson/put.gd-desktop/pull/1253).
The documentation companion is
[PR #1254](https://github.com/patrick-hudson/put.gd-desktop/pull/1254), head
`a2f80b794dc88526c38b0633d600135c887210b9`. Both target nightly and were open,
non-draft, CLEAN and MERGEABLE when verified on 2026-11-07. They were left
unmerged for the user. Merge the code PR first, then the documentation.

## CI

[Final code CI run 42408655973](https://github.com/patrick-hudson/put.gd-desktop/actions/runs/42408655973)
passed at the exact code head above. Ubuntu 24.04 passed **130/130** CTest suites;
Ubuntu 26.04 passed **133/133**, including the dark/light catalog and 150% layout
checks. Both passed on the first attempt, with no test retries. The contracts
job and required CI summary also passed. Packages, sanitizers and PipeWire were
not selected for these changed paths, so no results from those lanes are claimed.

[Documentation CI run 42407579882](https://github.com/patrick-hudson/put.gd-desktop/actions/runs/42407579882)
passed contracts and the required CI summary at the exact documentation head.

CodeRabbit and Cubic checks passed for both PRs. The code PR had no inline
review findings. The documentation PR's one finding compared the text against
the old code; its thread was answered with the linked implementation and resolved.
The advisory docstring-percentage warning was reviewed and explained on the code
PR; no public API contract was added by this artwork change.

## Reference update and first-run failure

[Initial CI run 42407538069](https://github.com/patrick-hudson/put.gd-desktop/actions/runs/42407538069)
failed only the two intended `settings-tray-seasons` image comparisons. Each
complete 223-state catalog matched 222 states and differed only in that image.
The retained expected/actual/diff images and reports preserve the failure.

Every changed pixel was verified to lie inside a December icon rectangle; turkey
artwork and text were unchanged. The unchanged repository reference-update tool
validated the full manifests and updated exactly the two dark/light reference
PNGs. It ran in the existing Ubuntu 26.04 container on Aurora with Pillow/numpy.
The copied results were checked byte-for-byte against the CI renders before
commit `5f469b332`. The subsequent full CI run passed them.

The main record's Aurora sample remains artwork/tray-transport evidence only.
These CI results add full source-build and automated contract coverage; they do
not turn that sample into package or cross-desktop release acceptance.
