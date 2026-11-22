# Follow-up: downloaded SHA-1 of a final-head large file

After B2's daily download cap reset, the kept final-head upload `r1792-final-keep200-1.bin` was downloaded and hashed on 2026-11-22 at 00:10Z. It is 200 MiB, sent on 4 connections in 59.6 s by `26.1121.6113-dev+gd816e1c447c5`, PR #1798's head. Its SHA-1 and byte count match the local file (`results/final-keep200-recheck.json`), so the download-cap gap in the README is closed for the final build. Afterwards, the object and its local copy were deleted, and the prefix was checked empty.
