# An upload whose final History write is refused stays active until it lands (#1579)

Picture and fault-shim results for put.gd-desktop PR #1616 after its redesign. Host: d69 (Debian 13,
Qt 6.8.2), ASan build at branch `fix/history-terminal-write-retry` e1d2050b7, private `dbus-run-session`,
offscreen QPA, the opaque test provider and the loopback custom-uploader fixture. No real cloud account.

- `finishing-annotated.png`: the upload has ended but the History database refused its final write. The
  operation stays in progress ("Finishing · Saving the result to History…"); its saved row still says
  Uploading until the same final write is retried and lands.

Fault shim (`tools/lab/faults/faultshim.c`): a 6 MiB `upload.files`, then
`rule write,truncate,fallocate,fsync history.sqlite 1.0 EIO` after 0.4 s (and 0.1 s), lifted 30 s later.

| Fault after | During the fault | After the lift |
| --- | --- | --- |
| 0.4 s | `running/finishing`, `activeOperations` 1, `unsavedResults` 1 | row `uploaded`, operation `failed` (`history_io`, the outcome its run chose), server holds the file, not active |
| 0.1 s | `stored/finishing`, `activeOperations` 1, `unsavedResults` 1 | operation `failed` (`history_io`), nothing on the server, Retry offered |
