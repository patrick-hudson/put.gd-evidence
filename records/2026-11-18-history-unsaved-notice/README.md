# History couldn't save a result: one notice, Retry refused until a restart (#1579)

Evidence for the put.gd-desktop PR that replaces #1616. Host: d69 (Debian 13, Qt 6.8.2), ASan build at branch
`fix/history-unsaved-notice` 05e088f05, private `dbus-run-session`, the loopback custom-uploader fixture. No real cloud account.

Fault shim (`tools/lab/faults/faultshim.c`, #1585): a 6 MiB `upload.files`, then
`rule write,truncate,fallocate,fsync history.sqlite 1.0 EIO` after 0.4 s (and 0.1 s), lifted afterwards.

| Fault after | During and after the fault (same session) |
| --- | --- |
| 0.4 s | `diagnostics.unsavedHistoryResults` 1, nothing active; the saved row stays `running/uploading` (the known limit), the server holds the file |
| 0.1 s | `unsavedHistoryResults` 1, nothing active; the saved row stays `stored/saving_local`, nothing on the server |

`notification-captured.jsonl`: the one notification the resident sent in the 0.4 s run (notifications turned on),
recorded by a minimal `org.freedesktop.Notifications` server on the private session bus. A restart's recovery
fixing the row is covered by the unit test `unsavedHistoryResultIsRememberedAndFixedByARestart`.
