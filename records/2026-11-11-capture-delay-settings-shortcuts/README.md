# Capture delay section in Settings → Capture

Picture for the put.gd-desktop change that adds a Capture delay section to
Settings → Capture: the "Wait before capturing" choice (None, 3, 5 or 10 seconds)
and the "Also delay captures started by a shortcut" checkbox
(`preferences.captureDelayShortcuts`, off by default).

- Source: put.gd-desktop branch `feat/shortcut-capture-delay`, commit `adbea240c`.
- Render: `putgd-ui-catalog` (dark scheme) through `tools/ci/check_catalog_render.py`,
  offscreen, built with the `dev` preset on the Debian 13 builder (d69). This is a
  synthetic catalog render, not a desktop acceptance run.
- `settings-capture-delay-annotated.png`: the catalog's `settings-capture-delay.png`
  with a red box and arrow drawn around the new section.

Tests run on that build (all passed): `settings_contract`, `capture_delay_contract`,
`gui_tray`, `gui_settings_*`, `operations_contract`, `config_reload_integration`,
`cli_integration`, `resident_session_contract`, `session_client_integration`,
`editor_contract`, `json_ref_lifetime_contract`.
