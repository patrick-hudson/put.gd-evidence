# #2028 error and failure messages: full before/after tables

The full string tables for the four pull requests that reword put.gd's error and failure
messages to the interface wording guide (`docs/design/voice.md`), split by source area:
app and core (`app.md`), storage drivers (`storage.md`), platform adapters and recording
(`platform.md`) and UI (`ui.md`). Each row is one changed string literal, taken from the
branch diff against nightly. `token-check-*.txt` is the output of `token_check.py`, which
checks that every failure code, placeholder, permission, path, number, unit and link in an
old string is still in its new hunk; each reported loss is explained in its pull request.
The scripts that produced both are included.
