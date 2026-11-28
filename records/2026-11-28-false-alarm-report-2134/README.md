# Not sensitive saves a false-alarm report: live check on Plasma and GNOME (#2134, PR #2140)

What was tested: the sensitive text check's new **Not sensitive** action, on the panel and in the editor the check opens, and its report in a diagnostics package. Every picture shows a synthetic dashboard made for this check (`scene.py` values only, labelled "synthetic test data"). No report image, corpus image or personal screen is published here.

**Build:** the PR's CI packages, `26.1128.7345-dev+gdf1e47962265`. That is CI's merge of PR head `bf4cd8ed8` into nightly (git tree `9126f7659839a1863b7df6063f0a922a03321f68`). The commits after it change only the MCP helper.

**Hosts:** each ran under `desktop_lock.py run` on the lab wall. A private put.gd resident of the installed package ran on the real display, with its own XDG folders and a synthetic S3 destination that was never used. The nightly packages were put back afterwards.
- k72: Kubuntu 26.04 Plasma Wayland, Qt 6.10.2, `putgd_26.1128.7345~dev+gdf1e47962265_amd64.deb`.
- f44: Fedora 44 GNOME Wayland, AppIndicator tray active, `putgd-26.1128.7345~dev+gdf1e47962265-1.fc44.x86_64.rpm`.

**Steps and results.** Clicks are real pointer input through the wall's VNC, at button positions read from the frames.

1. A desktop capture of the dashboard: the check found 8 phone numbers, all false alarms. Examples are "200 63292", a status and byte count, and "7162433", a units column. The panel opened.
2. Clicking **Not sensitive** saved a report: `reportedFrom: prompt`, `rule: phone`, Tesseract 5.5.0 on k72 and 5.5.4 on f44. The panel showed "Report saved for diagnostics." and the operation stayed `sensitive_text_found`. The capture was then cancelled: a real click on the panel's Cancel on f44, and via the CLI on k72, where the frame's text recognition missed the button.
3. A second capture, then **Open in editor**, then the editor's **Not sensitive**: a report was saved with `reportedFrom: editor`. `editor.inspect` showed `falseAlarm.state: saved` with the report's name.
4. A third capture, the editor's **Not sensitive**, then the editor's cancel 0.15 s later. It ended `cancelled` in 0.32 s on k72 and 0.31 s on f44, with no error and no `editor_exit`. On k72 that report was dropped; on f44 it had already saved.
5. `diagnostics.bundle` held `false-alarms/<name>/original.png`, `covered.png` and `report.json` for every report (2 on k72, 3 on f44), with `falseAlarmReports.included` matching and `invalid: 0`.
6. Settings' **Create diagnostics package…** dialog said so before saving, in its Never line: "This package includes 2 false-alarm reports, with pictures of your screen and the text read from them…".

| Picture | What it shows |
| --- | --- |
| `k72-panel-not-sensitive.png` | The panel with the new Not sensitive button (Plasma) |
| `k72-panel-report-saved.png`, `f44-panel-report-saved.png` | After the click: the saved line, and the four choices unchanged |
| `k72-editor-not-sensitive.png` | The editor the check opened, with Not sensitive in the Redact tool's panel |
| `f44-editor-report-saved.png` | The editor after its Not sensitive: "Report saved for diagnostics." (GNOME) |
| `k72-package-dialog-notice.png` | The package dialog's notice before saving |
