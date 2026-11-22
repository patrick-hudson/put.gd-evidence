# Early storage destination acceptance

Physical desktop checks on 2026-11-22. This round used the two CI builds requested for early feedback. The result is partial acceptance coverage.

## Running build identities

The commit and tree in resident diagnostics matched each CI artifact manifest on all five desktops. GitHub built its synthetic merge commits with the requested PR head as the second parent.

| Candidate | CI run | Requested PR head | Running CI commit | Running CI tree | Package version |
|---|---|---|---|---|---|
| Nextcloud/WebDAV #1879 | [45008312929](https://github.com/patrick-hudson/put.gd-desktop/actions/runs/45008312929) | `c22dc4fb1df77f34827825748da01225eae91a5e` | `e87f44df76cfd564401856cd93f8bb787d126f45` | `50d82725a32fc08eb2f59f0316f0267a8d9c24f0` | `26.1122.6444~dev+ge87f44df76cf` |
| SFTP #1881 | [45008350155](https://github.com/patrick-hudson/put.gd-desktop/actions/runs/45008350155) | `c3d2334da66b331318c4fab9f4020d8011b8874b` | `da4088862ccbb5ca160117b984fd186b32a9148c` | `a8e19c19229dd9de1431ef45602000eea669ae62` | `26.1122.6442~dev+gda4088862ccb` |

| Host | Native session | Candidate packaging | Original system package |
|---|---|---|---|
| f44 | Fedora 44 GNOME Wayland with active AppIndicator | Fedora 44 RPM, privately extracted | No system putgd package |
| k72 | Kubuntu 26.04 Plasma Wayland | Ubuntu 26.04 DEB, installed | `26.1122.6374~dev+gffeead0fc1f3` |
| m74 | Linux Mint 22.3 Cinnamon X11 | Ubuntu 24.04 DEB, installed | `26.1122.6373~dev+gaa202c7a634c` |
| d69 | Debian 13 Plasma Wayland | Debian 13 DEB, privately extracted | No system putgd package |
| aurora-amd | Aurora Fedora 45 Plasma Wayland | AppImage | No system putgd RPM |

The private desktop sockets were 39 bytes. The separate offscreen editor annotation socket was 36 bytes. Both fit the Linux 107-byte limit.

## Observed results

**Pass** means the stated interaction was observed. **Partial** states the part observed. **Blocked** identifies a lab condition. **—** means unrun in this early round.

| SFTP #1881 | f44 | k72 | m74 | d69 | aurora-amd |
|---|---|---|---|---|---|
| 1. OpenSSH dependency | Pass, RPM requires client | Pass, DEB depends on client | Pass, DEB depends on client | Pass, DEB depends on client | Host client available, AppImage uses it |
| 2. Server URL paste and normalization | Pass | Partial, typed URL and left field | Partial, typed URL and left field | Partial, typed URL and left field | Partial, typed URL and left field |
| 3. Trust matching ED25519 key | Pass | Pass | Pass | Pass | Pass |
| 4. Password prompt and session upload test | Pass | Pass | Pass | — | Pass |
| 5. Test upload and link | — | Pass over trusted HTTPS | — | — | HTTP refused, HTTPS unrun |
| 6. Linked region and default browser | — | — | — | — | — |
| 7. Upload-only region | — | Partial, file uploaded and History offered Copy path. Clipboard and toast were unmeasured | — | — | — |
| 8. Delete original from History | — | Pass, public endpoint changed from 200 to 404 | — | — | — |
| 9. Cancel large upload | — | — | — | — | — |
| 10. Read-only and create folder | Pass, permission denied for `/ro` and Create folder plus retest passed | — | — | — | — |
| 11. Rotate and re-pin | — | — | — | — | — |
| 12. CLI and MCP lifecycle | — | — | — | — | — |

| Nextcloud/WebDAV #1879 | f44 | k72 | m74 | d69 | aurora-amd |
|---|---|---|---|---|---|
| 1. Nextcloud Files URL normalization | Pass, pasted | — | Partial, typed | Partial, typed | Partial, typed using untrusted listener |
| 2. Default-browser grant | Pass | — | Blocked, Firefox certificate warning | Pass with temporary Firefox ESR handler and private trust profile | — |
| 3. Cancel sign-in | — | — | Partial, first flow cancelled and showed the message | — | — |
| 4. Test upload and link | Pass | — | — | Pass | — |
| 5. Region share and anonymous browser | — | — | — | — | — |
| 6. History deletion and missing share | — | — | — | — | — |
| 7. Password, sharing and quota policies | — | — | — | — | — |
| 8. Untrusted issuer, SHA-256 and CA command | — | — | Partial, verified from Sign in | — | Partial, verified from Sign in |
| 9. Sign-out and Devices & sessions | Partial, cleanup reached Signed out. Devices & sessions unverified | — | — | Partial, cleanup reached Signed out. Devices & sessions unverified | — |
| 10. Manual app password | — | — | — | — | — |
| 11. WebDAV link and delete | — | Partial, Test upload and link passed | — | — | — |
| 12. WebDAV missing folder | — | — | — | — | — |
| 13. Allow plain HTTP | — | Partial, row appeared and plain HTTP was refused while unchecked | — | — | — |
| 14. CLI and MCP lifecycle | — | — | — | — | — |

## Findings and test limitations

- **SFTP checklist mismatch on aurora-amd.** On the #1881 AppImage, add SFTP at `192.168.68.71:18371`, use `putgd-pw` and `/upload`, trust the verified key, store the password for the session and pass Test upload. Enter `http://192.168.68.71:18377/sftp/` as Link address and leave the field. The checklist offered that HTTP base as an option. The form marked it invalid and asked for HTTPS. The candidate's SFTP form and validator require HTTPS. Kubuntu passed the alternate HTTPS test. [Screenshot](annotated/aurora-sftp-http-refused.png)
- **Mint browser trust.** Install the exported Caddy CA in Mint's system store. In Nextcloud use the trusted :18374 listener and choose Sign in. The expected account page would load in Firefox after browser trust is established. Firefox showed its certificate warning with the system CA alone. Debian passed the same flow after importing the same CA into a short-lived Firefox ESR profile. This was a lab browser trust issue.
- **Physical input and frame collection.** The Aurora RFB keysym route mangled punctuation on a typed URL. The same visible field accepted native evdev input. The first Fedora cover check was made with the Shell overview open, and the second leg excluded a persistent overlay above the tested app area. Four Debian OCR screen reads stalled, each using roughly 50% CPU. The coordinator stopped those exact PIDs. Later checks used cropped frames and CLI inspection. The retained helper notes require a timeout for future OCR reads.
- **AppImage CLI harness.** The first standalone extracted CLI on Aurora loaded the host Qt and failed on the Qt 6.12 symbol version. Using the matching CLI and libraries from the running image mount fixed the identity check without a system package change.

No product defect was confirmed in the observed cases. The remaining cells require follow-up desktop acceptance on the final candidate artifacts.

## Restoration

The exact original DEBs were reinstalled and verified on k72 and m74. The other three system package inventories stayed at their original state. Temporary system CAs were removed on f44, k72, m74 and d69, and the trusted listener returned to an untrusted state without the lab CA. Aurora did not receive a system CA. On d69 the original URI handler file was restored byte-for-byte, the temporary Firefox desktop entry was removed and the lab CA was deleted from the private browser profile.

Nextcloud quota remained `none`, sharing remained enabled and mandatory share passwords remained off. The SFTP host key was unchanged. The two empty folders created for the nested-folder test were removed. The one synthetic SFTP region uploaded in this round returned HTTP 404 after exact History deletion. Raw screenshots and put.gd editor annotations are in [screenshots](screenshots/) and [annotated](annotated/).

| Host | Last acceptance cleanup receipt, UTC |
|---|---|
| f44 | 10:20:51 |
| k72 | 10:10:38 |
| m74 | 10:10:21 |
| d69 | 10:17:56 |
| aurora-amd | 10:13:59 |

All acceptance leases were released before the nightly cutoff. The d69 receipt records exact PID and start-time identities for the coordinator's unrelated corpus helpers.
