# Native browser sealed viewer acceptance, initial candidate

Debian 13 native KDE Wayland. put.gd 26.1126.7184-dev+g088b612dfe44, tree f3552a236750367d09c2ad27fefe29eab9cb8852. Mozilla Firefox 153.5.0esr and Google Chrome 158.0.8127.88 (official Linux DEB, downloaded for test). Public B2 links, synthetic payloads, real History.openLink through the desktop portal, per-browser private profile and temporary default handler. Address bars are not present in the published crops. No live link keys or passphrases included.

| Browser behavior | Firefox | Chrome |
| --- | --- | --- |
| Plain text shown | Pass (visible) | Pass (visible) |
| PNG shown | Pass (visible) | Pass (visible) |
| PNG fit/actual zoom | Not independently witnessed (browser switched before click) | Pass (two crops; visibly changed scale) |
| HTML downloads instead of rendering | Pass (Download UI and exact source bytes) | Pass (Download UI and exact source bytes) |
| Binary downloads | Pass (exact source bytes) | Pass (Download UI and exact source bytes) |
| 3-second moving MP4 | Player and original frame visible; playback click not independently witnessed | Pass (actual playback, 0:00 and 0:01 frames differed) |
| Missing fragment | Pass, exact missing-key error | Not run |
| Wrong passphrase | Pass, exact error | Pass, exact error |
| Correct passphrase | Pass, protected synthetic text displayed | Pass, protected synthetic text displayed |

The uploaded video for the browser witness is a short moving excerpt of the 1 GB fixture, not proof of full split-video playback in these browsers. The actual full split video was separately tested through the CLI on WebDAV; Firefox's private-CA warning blocked its first attempt at browser playback.

The passphrase upload used a saved session passphrase, with its value generated in-process and typed only into visibly focused password fields. The native notification said **Send the passphrase separately**. A browser save-password prompt for an incorrect synthetic input was dismissed, not saved. Both Chrome and Firefox accepted the correct input afterwards.

All public B2 test uploads were deleted through exact History deletion acknowledgements and independently verified zero file versions remained in their unique prefixes. Browser handlers and isolated profiles were retired, original MIME handler restored. The Chrome package was installed solely for the requested real-browser checks, then removed along with its added dependency and source configuration. These are initial-build unannotated visual witnesses, not the requested final-head annotated pictures.
