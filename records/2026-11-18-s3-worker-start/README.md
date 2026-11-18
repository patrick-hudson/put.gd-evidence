# S3 worker that cannot start says why and to try again

Pictures for the put.gd-desktop PR that keeps the S3 worker's start failure reason. Host: d69 (Debian 13,
Qt 6.8.2), ASan build, private `dbus-run-session`, the fault harness's offline S3 oracle (#1585), no real
cloud account. The resident's open-file limit was capped at what it held plus 10 (`prlimit`), then a 6 MiB
file was uploaded to the S3 destination. History was then rendered offscreen from that run's own data folder.

- `before-annotated.png`: nightly S3 code. `s3_module_unavailable`, "S3 support is missing or incompatible;
  restart put.gd after an update. If it remains unavailable, reinstall this build of put.gd".
- `after-annotated.png`: branch `fix/s3-worker-start-reason` at 49320a00f. `s3_module_unavailable`, "S3 support
  could not start (pipe: Too many open files); try again", details `{"reason": "pipe: Too many open files"}`.
