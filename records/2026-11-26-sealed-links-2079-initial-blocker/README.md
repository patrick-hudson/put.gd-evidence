# Sealed links #2079 — initial native candidate blocker

This is a **failed, partial acceptance**, not a release pass. Nothing was built locally or changed in product code.

- CI run: 45778610390, PR head 20503ba4d5bea5a38396ee9e1792b52b8a67b1d1.
- Installed Debian 13 DEB: 26.1126.7184-dev+g088b612dfe44; build manifest commit 088b612dfe44cfef2395f870f5dfc262f6b912f9 (CI merge commit), tree f3552a236750367d09c2ad27fefe29eab9cb8852 matches requested head's tree.
- Host: d69, KDE Plasma Wayland, private native resident. Socket length: 60 UTF-8 bytes.
- AWS S3 live credentials were read in process from the protected builder input. No credentials, link keys or signed URLs are included.
- Test was confined to a new, initially empty synthetic prefix in the documented test bucket. The independent origin listing was empty at teardown. No other objects or bucket settings were touched.

## Reproduction

1. Install the CI Debian package and launch the resident in an isolated native desktop profile.
2. Configure an S3 destination: standard AWS endpoint, public-read ACL, public HTTPS link base, fresh acceptance prefix, session credentials.
3. Store credentials via the authenticated local session socket; setup completed.
4. Run `setup.testDestination` (the underlying Destinations → Test upload and link command) and inspect the setup job. Observe the seal result.
5. Open Destinations and query `ui.sealLinks` with action inspect.

Expected: ordinary test and seal test pass, Seal links can be enabled. Actual: ordinary setup completed, but seal result was `failed` with reason **Storage request does not match its supported schema**. UI agent state confirmed failed/unavailable and mode changes disabled. Subsequent public S3 sealed uploads require a passing check so these rows were blocked rather than reported as passes.

Read-only source inspection identifies a likely cause: the seal checker constructs a Destination with an empty profileRevision, while S3 worker decoding requires a nonempty profileRevision. The ordinary destination test supplies the current settings revision. This is a hypothesis based on the live error and code, not a tested fix.

See [d69-results.json](d69-results.json) for the sanitized observations. No graphical screenshot was retained for this first failing trial; the CLI/UI agent state establishes the failure, not a desktop visual pass. The candidate was removed, matching the acquire-time no-package state; desktop lock released verified-clean at 08:21:04 UTC (host receipt 2026-11-26T08-21-04Z-release.json).
