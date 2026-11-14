# Omarchy ELF dependency audit, pass four

All package paths came from pacman -Qlq putgd. Regular files and symlink targets were filtered by ELF magic. Full ldd/readelf stdout, stderr and return codes are in p4-elf-audit.json.

54 ELF paths; 30 distinct resolved files. Missing dependencies on 29 paths / 13 distinct files. Every missing name is libcrypto.so.4; each affected file directly lists that name as NEEDED. No ELF lists libssl.so.4 as NEEDED.

| Package-owned path | Resolved file | ldd missing names | Direct OpenSSL 4 NEEDED |
| --- | --- | --- | --- |
| /usr/bin/putgd | /usr/bin/putgd | none | none |
| /usr/bin/putgd-b2-worker | /usr/bin/putgd-b2-worker | none | none |
| /usr/bin/putgd-capture | /usr/bin/putgd-capture | none | none |
| /usr/bin/putgd-cli | /usr/bin/putgd-cli | libcrypto.so.4 => not found | libcrypto.so.4 |
| /usr/bin/putgd-clipboard-keeper | /usr/bin/putgd-clipboard-keeper | none | none |
| /usr/bin/putgd-http-worker | /usr/bin/putgd-http-worker | none | none |
| /usr/bin/putgd-ocr | /usr/bin/putgd-ocr | none | none |
| /usr/bin/putgd-record | /usr/bin/putgd-record | none | none |
| /usr/bin/putgd-region | /usr/bin/putgd-region | none | none |
| /usr/bin/putgd-s3-worker | /usr/bin/putgd-s3-worker | none | none |
| /usr/bin/putgd-ui | /usr/bin/putgd-ui | none | none |
| /usr/lib/caja/extensions-2.0/libputgd-caja.so | /usr/lib/caja/extensions-2.0/libputgd-caja.so | none | none |
| /usr/lib/nautilus/extensions-4/libputgd-nautilus.so | /usr/lib/nautilus/extensions-4/libputgd-nautilus.so | none | none |
| /usr/lib/putgd/libaws-c-auth.so | /usr/lib/putgd/libaws-c-auth.so.1.0.0 | libcrypto.so.4 => not found | libcrypto.so.4 |
| /usr/lib/putgd/libaws-c-auth.so.1.0 | /usr/lib/putgd/libaws-c-auth.so.1.0.0 | libcrypto.so.4 => not found | libcrypto.so.4 |
| /usr/lib/putgd/libaws-c-auth.so.1.0.0 | /usr/lib/putgd/libaws-c-auth.so.1.0.0 | libcrypto.so.4 => not found | libcrypto.so.4 |
| /usr/lib/putgd/libaws-c-cal.so | /usr/lib/putgd/libaws-c-cal.so.1.0.0 | libcrypto.so.4 => not found | libcrypto.so.4 |
| /usr/lib/putgd/libaws-c-cal.so.1.0 | /usr/lib/putgd/libaws-c-cal.so.1.0.0 | libcrypto.so.4 => not found | libcrypto.so.4 |
| /usr/lib/putgd/libaws-c-cal.so.1.0.0 | /usr/lib/putgd/libaws-c-cal.so.1.0.0 | libcrypto.so.4 => not found | libcrypto.so.4 |
| /usr/lib/putgd/libaws-c-common.so | /usr/lib/putgd/libaws-c-common.so.1.0.3 | none | none |
| /usr/lib/putgd/libaws-c-common.so.1.0 | /usr/lib/putgd/libaws-c-common.so.1.0.3 | none | none |
| /usr/lib/putgd/libaws-c-common.so.1.0.3 | /usr/lib/putgd/libaws-c-common.so.1.0.3 | none | none |
| /usr/lib/putgd/libaws-c-compression.so | /usr/lib/putgd/libaws-c-compression.so.1.0.0 | none | none |
| /usr/lib/putgd/libaws-c-compression.so.1.0 | /usr/lib/putgd/libaws-c-compression.so.1.0.0 | none | none |
| /usr/lib/putgd/libaws-c-compression.so.1.0.0 | /usr/lib/putgd/libaws-c-compression.so.1.0.0 | none | none |
| /usr/lib/putgd/libaws-c-event-stream.so | /usr/lib/putgd/libaws-c-event-stream.so.1.0.0 | libcrypto.so.4 => not found | libcrypto.so.4 |
| /usr/lib/putgd/libaws-c-event-stream.so.1.0 | /usr/lib/putgd/libaws-c-event-stream.so.1.0.0 | libcrypto.so.4 => not found | libcrypto.so.4 |
| /usr/lib/putgd/libaws-c-event-stream.so.1.0.0 | /usr/lib/putgd/libaws-c-event-stream.so.1.0.0 | libcrypto.so.4 => not found | libcrypto.so.4 |
| /usr/lib/putgd/libaws-c-http.so | /usr/lib/putgd/libaws-c-http.so.1.1.0 | libcrypto.so.4 => not found | libcrypto.so.4 |
| /usr/lib/putgd/libaws-c-http.so.1.1 | /usr/lib/putgd/libaws-c-http.so.1.1.0 | libcrypto.so.4 => not found | libcrypto.so.4 |
| /usr/lib/putgd/libaws-c-http.so.1.1.0 | /usr/lib/putgd/libaws-c-http.so.1.1.0 | libcrypto.so.4 => not found | libcrypto.so.4 |
| /usr/lib/putgd/libaws-c-io.so | /usr/lib/putgd/libaws-c-io.so.1.1.0 | libcrypto.so.4 => not found | libcrypto.so.4 |
| /usr/lib/putgd/libaws-c-io.so.1.1 | /usr/lib/putgd/libaws-c-io.so.1.1.0 | libcrypto.so.4 => not found | libcrypto.so.4 |
| /usr/lib/putgd/libaws-c-io.so.1.1.0 | /usr/lib/putgd/libaws-c-io.so.1.1.0 | libcrypto.so.4 => not found | libcrypto.so.4 |
| /usr/lib/putgd/libaws-c-mqtt.so | /usr/lib/putgd/libaws-c-mqtt.so.1.1.2 | libcrypto.so.4 => not found | libcrypto.so.4 |
| /usr/lib/putgd/libaws-c-mqtt.so.1.1 | /usr/lib/putgd/libaws-c-mqtt.so.1.1.2 | libcrypto.so.4 => not found | libcrypto.so.4 |
| /usr/lib/putgd/libaws-c-mqtt.so.1.1.2 | /usr/lib/putgd/libaws-c-mqtt.so.1.1.2 | libcrypto.so.4 => not found | libcrypto.so.4 |
| /usr/lib/putgd/libaws-c-s3.so | /usr/lib/putgd/libaws-c-s3.so.1.3.1 | libcrypto.so.4 => not found | libcrypto.so.4 |
| /usr/lib/putgd/libaws-c-s3.so.1.3 | /usr/lib/putgd/libaws-c-s3.so.1.3.1 | libcrypto.so.4 => not found | libcrypto.so.4 |
| /usr/lib/putgd/libaws-c-s3.so.1.3.1 | /usr/lib/putgd/libaws-c-s3.so.1.3.1 | libcrypto.so.4 => not found | libcrypto.so.4 |
| /usr/lib/putgd/libaws-c-sdkutils.so | /usr/lib/putgd/libaws-c-sdkutils.so.1.0.0 | none | none |
| /usr/lib/putgd/libaws-c-sdkutils.so.1.0 | /usr/lib/putgd/libaws-c-sdkutils.so.1.0.0 | none | none |
| /usr/lib/putgd/libaws-c-sdkutils.so.1.0.0 | /usr/lib/putgd/libaws-c-sdkutils.so.1.0.0 | none | none |
| /usr/lib/putgd/libaws-checksums.so | /usr/lib/putgd/libaws-checksums.so.1.0.1 | none | none |
| /usr/lib/putgd/libaws-checksums.so.1.0 | /usr/lib/putgd/libaws-checksums.so.1.0.1 | none | none |
| /usr/lib/putgd/libaws-checksums.so.1.0.1 | /usr/lib/putgd/libaws-checksums.so.1.0.1 | none | none |
| /usr/lib/putgd/libaws-cpp-sdk-core.so | /usr/lib/putgd/libaws-cpp-sdk-core.so | libcrypto.so.4 => not found | libcrypto.so.4 |
| /usr/lib/putgd/libaws-cpp-sdk-s3.so | /usr/lib/putgd/libaws-cpp-sdk-s3.so | libcrypto.so.4 => not found | libcrypto.so.4 |
| /usr/lib/putgd/libaws-crt-cpp.so | /usr/lib/putgd/libaws-crt-cpp.so | libcrypto.so.4 => not found | libcrypto.so.4 |
| /usr/lib/putgd/libputgd-s3.so | /usr/lib/putgd/libputgd-s3.so | libcrypto.so.4 => not found | libcrypto.so.4 |
| /usr/lib/putgd/libs2n.so | /usr/lib/putgd/libs2n.so.1.0.0 | libcrypto.so.4 => not found | libcrypto.so.4 |
| /usr/lib/putgd/libs2n.so.1 | /usr/lib/putgd/libs2n.so.1.0.0 | libcrypto.so.4 => not found | libcrypto.so.4 |
| /usr/lib/putgd/libs2n.so.1.0.0 | /usr/lib/putgd/libs2n.so.1.0.0 | libcrypto.so.4 => not found | libcrypto.so.4 |
| /usr/libexec/putgd/proton/putgd-proton-runtime | /usr/libexec/putgd/proton/putgd-proton-runtime | none | none |

## Version/load checks

| Program | --version-json exit | Result |
| --- | --- | --- |
| putgd | 0 | 26.1114.5000-nightly / df229be2990554bb9c4dff5a020e1407e4eb1885 |
| putgd-cli | 127 | /usr/bin/putgd-cli: error while loading shared libraries: libcrypto.so.4: cannot open shared object file: No such file or directory |
| putgd-ocr | 0 | 26.1114.5000-nightly / df229be2990554bb9c4dff5a020e1407e4eb1885 |
| putgd-ui | 0 | 26.1114.5000-nightly / df229be2990554bb9c4dff5a020e1407e4eb1885 |
| putgd-region | 0 | 26.1114.5000-nightly / df229be2990554bb9c4dff5a020e1407e4eb1885 |
| putgd-record | 0 | 26.1114.5000-nightly / df229be2990554bb9c4dff5a020e1407e4eb1885 |
