# Final public split, refusal and cancellation results (e910)

CI package 45789606403, head e910ab333f91f710e818ba5d69a638d57403e5af,
version 26.1126.7192-dev+gf977a6911c14,
gitTree 58f251154db252458bb8d6ff804de1ed5bf19a23, Debian 13 Plasma
Wayland, no local build. Fixture: 1,061,463,118-byte moving H.264
video, SHA-256 baade7cf41e68b458c6c904a2208286663677c8774e2755ad806182069b2d3d3.

- S3 public and R2 public: 1 GB sealed upload, two same-stem random
  HTML/BIN files, exact CLI open SHA, terminal Delete journal completed,
  remoteStatus removed, sealDataStatus removed, empty prefix.
- B2 public retry: same result. Terminal Delete operation 8371d2a9-bb41-4011-b6c3-7341217ff5f3;
  independent B2 version and unfinished-large-file list both zero. The
  first attempt had only 4.8 MB uploaded in four minutes (TCP delivery
  rate 153 kbps, congestion window 2, heavy retransmission). It was
  cancelled explicitly and both independent lists were zero. Fresh
  attempt on a healthy endpoint completed; classify the first attempt
  as a transient lab route problem, not a reproducible product failure.
- S3 presigned and B2 authorized: same video refused with
  seal_split_unavailable; Retry gave the same refusal. Prefix empty
  both times. B2 authorized used a scoped public-only lab bucket with
  shareFiles permission and actual authorization query; private-bucket
  enforcement could not be verified without a private lab bucket.
- File 2,147,483,649 bytes: seal_too_large, Retry same, prefix empty.
- Turned Seal mode Off and uploaded the original 1 GB via S3 presigned:
  completed and copied an ordinary link without a fragment; terminal
  History Delete completed and prefix empty.
- Repeated old Chrome viewer on an independently generated e910 page:
  original file SHA matched on CLI open, portal opened Chrome, page
  reported decrypted but player remained black at 0:00 after play.
  Both split files deleted via terminal History Delete, prefix empty.
  Exact e910 before picture is in the next viewer follow-up.

Evidence: d69-public-large-e910-results.json, d69-r2-large-e910-results.json,
d69-b2-public-retry-e910-results.json, d69-b2-public-retry-unfinished-results.json,
d69-b2-authorized-e910-results.json, d69-presigned-large-e910-results.json.
