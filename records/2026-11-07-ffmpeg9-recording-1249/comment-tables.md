**Mint 22.3 Cinnamon X11 — m74: PASS**

| Format | Motion candidate / baseline | A/V ms candidate / baseline¹ | Pause/resume |
|---|---:|---:|---|
| MP4 | 18.848 / 18.801 | 16.000 / 16.000 | PASS |
| WEBM | 18.812 / 18.803 | -0.500 / -0.500 | PASS |
| GIF | 18.651 / 18.684 | N/A — silent | PASS |
| WEBP | 18.708 / 18.674 | N/A — silent | PASS |

**Kubuntu Plasma Wayland — k72: PASS**

| Format | Motion candidate / baseline | A/V ms candidate / baseline¹ | Pause/resume |
|---|---:|---:|---|
| MP4 | 20.003 / 20.107 | 28.700 / -4.000 | PASS |
| WEBM | 20.107 / 19.897 | 19.500 / 19.500 | PASS |
| GIF | 19.712 / 19.660 | N/A — silent | PASS |
| WEBP | 19.790 / 19.724 | N/A — silent | PASS |

**Aurora KDE Wayland — aurora-amd: FAIL (HEVC VA-API)**

| Format | Motion candidate / baseline | A/V ms candidate / baseline¹ | Pause/resume |
|---|---:|---:|---|
| MP4 | 20.126 / 19.982 | 29.300 / 29.300 | PASS |
| WEBM | 19.988 / 19.994 | 35.500 / 35.500 | PASS |
| GIF | 19.723 / 19.749 | N/A — silent | PASS |
| WEBP | 19.889 / 19.991 | N/A — silent | PASS |

**Ubuntu GNOME Wayland VM on d69: BLOCKED / partial**

| Format | Motion candidate / baseline | A/V ms candidate / baseline¹ | Pause/resume |
|---|---:|---:|---|
| MP4 | 25.813 / 25.809 | 46.000 / 46.000 | PASS² |
| WEBM | 26.029 / 25.919 | 55.500 / 55.500 | PASS² |
| GIF | — / — | N/A — silent | BLOCKED (disk reserve)² |
| WEBP | — / — | N/A — silent | BLOCKED (disk reserve)² |

**Fedora GNOME — f44: NOT RUN**

| Format | Motion C / B | A/V C / B | Pause/resume |
|---|---|---|---|
| MP4 | NOT RUN | NOT RUN | NOT RUN |
| WebM | NOT RUN | NOT RUN | NOT RUN |
| GIF | NOT RUN | NOT RUN | NOT RUN |
| WebP | NOT RUN | NOT RUN | NOT RUN |

The live `codex-pr1247-ab` desktop lock refused acquisition; it was never broken. Digests were verified read-only. NVENC is **NOT RUN — no lab NVIDIA hardware**.
