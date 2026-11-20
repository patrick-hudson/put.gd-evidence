# Random names: UUID or random characters (#1729)

Settings → Capture → File names, rendered by `putgd-ui-catalog` (offscreen, dark theme) on k72 from branch
`feat/random-name-styles` at 4713a41d9 (based on nightly 2c4d0b27a).

- `random-name-uuid.png`: Naming set to Random names shows the new **Random name** row; UUID stays the default.
- `random-name-characters.png`: Random characters adds **Length** (4 to 64, default 12), **Include capital letters**
  and **Include numbers**. Lowercase letters are always used.

The gold boxes mark the new rows. Tests on k72 at the same source: test_upload_naming, test_settings,
test_collision_policy, test_operations, gui_settings_capture and gui_settings_general all passed.
