# Large split, oversize refusal, and controlled HTTPS retry

Candidate build 26.1126.7184-dev+g088b612dfe44 (tree f3552a236750367d09c2ad27fefe29eab9cb8852; CI 45778610390), installed DEB on d69 native KDE Wayland and k72 native KDE Wayland.

## WebDAV large split and pre-existing safe-delete limit

Generated a moving 100-second MP4 using FFmpeg testsrc2, 1920x1080 at 30 fps, H.264, 1,061,463,118 bytes, SHA-256 baade7cf41e68b458c6c904a2208286663677c8774e2755ad806182069b2d3d3. It was encoded on d69 under a quiet lease, not on the workstation.

- WebDAV split upload via `putgd-cli upload --seal` completed and copied. Independent origin listing returned exactly two objects, matching 12-character alphanumeric stem, extensions .html and .bin. History fragment format correct. `putgd-cli open -` restored the original SHA-256.
- **Deletion row failed at origin:** page removed, data left, remoteStatus unknown, error seal_data_left. Nested dataStatus unknown/dataError unsupported_capability (reason identity_unconfirmed): the server did not return an ETag for the data file. In the deletion journal, sealDataStatus unknown, no sealDataProgress, page progress done. Exact Retry deletion after credential reload was accepted, returned the same error. The encrypted data file SHA matched its own receipt; tester manually removed that exact file and empty collection and independently verified absence.
- **Nightly comparison:** installed published 26.1125.7045-nightly, tree c05b34b4832bf8265165b0062953c09295a8e05f, exact release DEB SHA-256 dde5dfb7cb1bccea69231eb378f02e3baecaf330b801e60d6dff32e9f0c8a767. Same moving file ordinary upload completed, lacked concurrencyToken, delete.prepare refused unsupported_capability. Thus the server/provider large-file identity limitation predates sealing. Candidate and nightly share the 256 MiB cap on fallback ETag content verification. The nightly owned file SHA matched the source, was manually removed, and folder absence verified.
- 2,147,483,649-byte synthetic sparse file: candidate upload refused seal_too_large; Retry returned same code. Only the already-recorded large data file remained at origin; no new object was created. Its cleanup is covered above.
- Initial native TLS attempt failed because the copied lab CA was not in distro trust; temporary installation of the exact lab CA succeeded, and removal/restoration verified afterwards. Firefox still refused the privately issued lab CA; no bypass attempted. Public browser testing separate.
- Nightly before image: [d69-nightly-before.png](d69-nightly-before.png), showing the connection test at the end of the card without Seal links. Unannotated crop.

## Controlled custom uploader over HTTPS

Real loopback HTTPS server in the lab, with a temporary generated certificate trusted by the distro during the run; not the documented third-party service. The product's imported custom-uploader driver uses real multipart HTTPS, returns exact uploaded bytes as inline text/html, and exposes an object-specific deletion URL. No product changes or remote user content.

- Test and seal passed, probe cleanup removed, receiver empty.
- Deliberate 500 after reading half the upload body; did not store any object. Upload returned http_outcome_unknown and retained the sealed page/key. Retry succeeded; same key and stored page SHA, origin page SHA identical. CLI open restored exact original. A separate synthetic copy with a one-byte static viewer change was refused with seal_page_changed, no output created. Copy was removed.
- History deletion reached removed/done; independently empty receiver after cleanup, stopped server, removed the exact temporary CA, removed generated TLS private key.
- Documented XBackBone receiver on k72: both exact candidate and exact published nightly failed the **ordinary** connection test with http_outcome_unknown before the seal stage. Lab receiver storage had zero files before and after each. Therefore no new sealed-specific conclusion from XBackBone; receiver pods were stopped, preserving existing volumes. This contrasts with the explicit HTTPS receiver's passing seal check.

See sanitized JSON rows for precise identities. Unlike a product mock, the custom receiver exercises the installed production uploader over real TLS and HTTP, but it is a controlled acceptance fixture, not proof of any specific third-party receiver.
