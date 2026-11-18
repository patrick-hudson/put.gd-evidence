# An upload History could not record is recovered in place (#1579)

Picture and fault-shim results for put.gd-desktop PR #1616 after its third design (in-process recovery). Host: d69
(Debian 13, Qt 6.8.2), ASan build at branch `fix/history-terminal-write-retry` b9105400d, private `dbus-run-session`,
offscreen QPA, the opaque test provider and the loopback custom-uploader fixture. No real cloud account.

- `recovered-annotated.png`: the upload ended while History refused writes. The operation stopped as after a crash,
  and once History could be written again put.gd applied startup recovery to it alone: interrupted, its upload
  outcome unknown, with Retry upload (which reconciles it with the destination before sending anything).

Fault shim (`tools/lab/faults/faultshim.c`): a 6 MiB `upload.files`, then
`rule write,truncate,fallocate,fsync history.sqlite 1.0 EIO` after 0.4 s (and 0.1 s), lifted 30 s later.

| Fault after | During the fault | After the lift |
| --- | --- | --- |
| 0.4 s | `activeOperations` 0 (the slot is free), saved row `running/uploading` | `interrupted`, item `unknown`, server holds the file |
| 0.1 s | `activeOperations` 0, saved row `running/preflight` | `interrupted`, item `stored`, nothing on the server |
