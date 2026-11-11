# Scroll capture: second physical acceptance pass, PR #1398

Acceptance remains **blocked** by the native text-view cases and Stop retaining an earlier viewport on d69. The ruler, long-page, fractional-scale, browser, and GNOME start-race fixes passed the counted checks below. No false end_of_content was observed in a correctly framed ruler run. No product code was edited, compiled, committed or pushed, and no VM was touched.

PR head: `289a611894100f8f0427688bd4fd739f6334a56d`. CI run `42921514454` completed successfully before package download/install. Installed version `26.1110.4640~dev+ga4b85216509c` identifies GitHub merge `a4b85216509cbc23af785eb2266451d5447e2079`, whose PR parent is that head; this is expected. Full source/tree/parent identities are in [SOURCE.txt](SOURCE.txt), package build metadata in [packages](packages), and checks in [ci-checks.txt](ci-checks.txt).

| Package | SHA-256 |
| --- | --- |
| Debian 13 DEB, installed on d69 | `96ff09b3773fa6c28798fafa025b48671408ba957a7b71d3deb11a22fb4f986f` |
| Fedora 44 RPM, installed on f44 | `5d498dccb78ec898c01fe14ac9ff5f5248b32f7e141560dbc7ec9d9f4506f412` |
| Ubuntu 24.04 DEB, downloaded for Mint, not installed in this publication | `97f0723ebd11b68901fbf8e2d0cc2230020a6576a849459fdee03a8fd2592b1b` |

| Host / desktop | Case | Count and endReasons | Result / evidence |
| --- | --- | --- | --- |
| d69 Debian 13, Plasma 6.3.6 native Wayland | Consecutive 2,400 px native Qt ruler | **20/20 exact**, 20 end_of_content | [plain-00](d69/plain-00/result.json) through plain-19; every PNG and helper log retained |
| d69 | 24,000 px page, maxHeight 40,000 | **3/3 exact**, 3 end_of_content | [long-00](d69/long-00/result.json) through long-02, full 960 × 24,000 |
| d69 | Default cap on 40,000 px page, warning and upload | **1/1**, height_cap | Exact 960 × 30,000 prefix, saved notification, isolated loopback receipt; [cap-00](d69/cap-00/result.json) |
| d69 | 125% output scale | **3/3 exact within 1 physical px tolerance**, 3 end_of_content | 1200 × 3000, zero bad scanlines; [scaled-00](d69/scaled-00/result.json) through scaled-02 |
| d69 | Full-size native GTK 4 TextView, 1,500 numbered lines, 1900 × 1080 selection | **0/3 complete**, 3 lost_track | Ambiguous first step; [gtkfull-00](d69/gtkfull-00/result.json) through gtkfull-02 |
| d69 | Full-size native QPlainTextEdit, 1,500 numbered lines, 1900 × 1080 selection | **0/3 complete**, 3 lost_track | Ambiguous first step; [qtfull-00](d69/qtfull-00/result.json) through qtfull-02 |
| d69 | Same full-size Qt view, narrower 600 × 1080 selection (diagnostic control) | **3/3 complete**, 3 end_of_content | Every one of 1,500 line bands once, constant 18 px pitch, zero duplicates/gaps; [qtnarrowfull-00](d69/qtnarrowfull-00/result.json) through qtnarrowfull-02 |
| d69 | Firefox kiosk ruler, 14 s startup wait | **3/3 exact**, 3 end_of_content | [firefox-00](d69/firefox-00/result.json) through firefox-02; viewport-height selection |
| d69 | Agent-only official-SDK MCP, production CLI, fetched PNG | **1/1 exact**, end_of_content | [MCP transcript](d69-mcp.json), [PNG verification](d69/mcp/result.json) |
| d69 | Stop while scrolling to top | **0/1 current-viewport correct**, stopped | Returned exact earlier viewport 23,400 rather than visible 21,600; [adjudication](d69/stop-top2/adjudication.json). Early-stop control 1/1 returned unchanged viewport with stopped. |
| d69 | Cap warning removed for next capture | **1/1**, next capture end_of_content | [clear-00](d69/clear-00/result.json), saved next ready/capturing frames show no prior warning |
| d69 | Safe shortcut Ctrl+Shift+F7 + real VNC drag | **1/1 exact**, new uploaded operation | [history/PNG identity](d69/user/result.json), user-selector.png and user-05.png (Capturing, ring and bar) |
| d69 | Tray entry, Settings fields, cap notification | **3/3 visuals saved** | tray-menu.png includes Capture scrolling region, 30000 and Scroll to the top first; cap-notification.png |
| f44 Fedora 44, GNOME 50.6 native Wayland | Immediate scroll.start after ready | **5/5 exact**, 5 end_of_content | No fixed start delay; [race2-00](f44/race2-00/result.json) through race2-04; [timing](f44/race-start-timing.json) |
| f44 | Clean native GTK ruler | **3/3 exact**, 3 end_of_content | [gtkclean-00](f44/gtkclean-00/result.json) through gtkclean-02; zero unexpected barcode-interior pixels |
| f44 | Firefox kiosk ruler, 14 s wait | **3/3 exact**, 3 end_of_content | [firefox-00](f44/firefox-00/result.json) through firefox-02 |
| f44 | Agent-only MCP, fetched PNG | **1/1 exact**, end_of_content | [transcript](f44-mcp.json), [verification](f44/mcp/result.json); no notification shadow |
| f44 | User-style safe shortcut + real drag | **1/1 exact**, new uploaded operation | [verification](f44/user/result.json), user-selector.png and user-05.png show capture-phase ring/bar |
| f44 | Cap, warning, upload; tray entry; Settings fields | **1/1 cap**, height_cap; **3/3 visuals** | Exact 30,000 px prefix; [cap-00](f44/cap-00/result.json); cap-notification.png, tray-menu.png, settings-fields-both.png |
| m74 Cinnamon X11 | Three Firefox runs and one plain ruler | **not run: desktop held by another session** | Final check after publication still held by claude-history-lab-recipes. Firefox 0/3 attempted, plain 0/1 attempted. [Final disposition](CINNAMON-final.md); no current-head Cinnamon pass is claimed. |

## Failures and attribution

**d69 text matching:** six corrected full-height wide selections end lost_track after one viewport. GTK source summaries are fresh/quiet **2/1, 1/0, 1/0**; Qt **1/0, 1/0, 1/0**. Each has one retry and no scroll-back, and the terminal note is “first step is ambiguous (periodic or blank content) and no px-per-notch is known”. This is the matcher/first-step recovery path, not evidence of a stalled frame stream or a wrong admitted stitch. The narrow Qt control passes all 1,500 lines; it does not clear the full-width failures. Narrow GTK diagnostic attempts also failed lost_track (NoMatch and recovery scroll-backs). Every failure's complete source summary is retained in its result.json and helper.log, with its PNG. [counts.json](d69/counts.json) lists individual outcomes and source lines, including earlier diagnostic crops.

**d69 Stop/final frame:** stop-top2 sent Stop after two wheel-up batches. The owned fixture log records/repaints 22,500 then 21,600; the result remains a 600 px image starting at 23,400. Its source summary is fresh **0**, quiet **0**, unproven **0**, retries **0**. The retained PNG is internally exact, but not the current viewport required by this gate. The original pixel-only pass in result.json is explicitly superseded for functional acceptance by adjudication.json. The earlier .05 s stop returned the unchanged viewport correctly; it does not establish the later phase.

**Harness/prerequisites, preserved:** setup initially hit a non-PID /proc entry and a missing module main guard, before any capture. Five f44 attempts were refused before the helper with region_unavailable / gnome_login_required, loaded 0: not start-race failures. After checking that no Patrick apps were running, the resident was stopped, GDM restarted, Activities exited visibly, and extension 22 verified ACTIVE and setup ready before the counted five. Those original refusals and logs are retained under race-00..04 (no PNG or source line exists because capture never began).

The first text crop was 1040 px tall on a 1080 px viewport. Narrow Qt outputs then omitted the bottom 40 px, so its three 1498-band images are invalid harness framing, not complete text acceptance or demonstrated false bottom. Corrected full-height narrow Qt gives all 1500 bands. Both attempts remain. An initial user-PNG byte comparison reused d69's hash on Fedora, where label fonts differ; pixel verification corrected that harness check and passes. Re-export manifest self-inclusion was corrected; exported payload hashes were checked after transfer. There was no Ctrl+Alt+F-key binding, VT switch, display-server permission bypass, mock desktop evidence or product compilation.

## Method and restoration

All testing ran on the physical desktops through their existing localhost VNC listeners and wall tunnels, with saved visuals per capture. The Qt and GTK fixtures are native Wayland clients. Ruler verification checks every scanline plus barcode cell interiors; fractional verification independently checks row centres and all physical scanlines within the stated one-pixel tolerance. Text verification requires exactly 1500 distinct whole line bands, one constant pitch, no duplicate and no gap. All resolved session sockets were 46 UTF-8 bytes, checked before isolated resident launch. Profiles, archives, synthetic HTTP receivers and logs are private under `/home/patrick/work/p21398` on each tested host; uploads went only to that host's 127.0.0.1:19399. No credentials or user objects were involved.

Both installed test packages were removed (without purging configuration), all owned residents/helpers/fixtures/receivers stopped, the private shortcut reset, and d69 scale restored to 1. No package was installed on m74. GNOME AppIndicator enablement for the tray photo was reversed. GNOME was re-logged in after RPM removal to return to the baseline without the loaded package extension; no Patrick apps were present before either restart. d69 remained on active tty1, f44 on active tty2, with fgconsole checked. [d69 lease receipt](d69-release.json) and [f44 lease receipt](f44-release.json) show successful cleanup and release, both before 00:00 UTC, well before 07:15 UTC.

Left behind: raw evidence and isolated profiles/packages under `/home/patrick/work/p21398` on d69 and f44; d69 also has the initial scripts-only staging directory `/tmp/p21398`. Existing projects, user data, signing agent, wall services/tunnels, VMs and goldens were preserved. All exported files were checksum verified; raw host evidence remains available. This bounded feature pass is not release acceptance or a memory gate. Cinnamon's final lock disposition is recorded separately as requested by Patrick.
