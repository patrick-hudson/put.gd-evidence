# Revised candidate recheck commands

Run from the workstation checkout. Stage the candidate Ubuntu 24.04 DEB and the Mint driver and crop definitions under the existing private `/tmp/qr1863` root on m74 with `remote.sh`. Check the candidate DEB SHA-256 against the staged copy. Acquire the m74 desktop lock before changing packages or opening fixtures. Read the apt simulations before installation and removal, and use the quiet-lease guard before each heavy command.

```sh
gh run download 44994509136 -n release-native-ubuntu24.04 -D CANDIDATE_ARTIFACT_DIRECTORY
python3 tools/lab/desktop_lock.py guard m74 --session codex-qr1863 &&
  ./remote.sh m74 'umask 077; python3 /tmp/qr1863/desktop-review.py m74 recheck 1 3 4 6 5-jwt 5-jwt-labeled 5-hex 5-hex-three a-dot-jwt b-long-jwt c-loose-hex'
python3 scripts/verify.py m74/recheck scripts/regions-m74.json
```

The staged driver is `scripts/desktop.py`. It checks the exact runtime build commit and tree before opening any fixture and enforces the 107-byte session-socket limit. Both HTML fixtures use actual CSS wrapping in Firefox. The long JWT is one logical xed line. For the JSON evidence, `prepare_evidence.py` preserves word geometry and splits the synthetic OCR strings into independently stored pieces.
