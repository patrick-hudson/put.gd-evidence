# Results

## Key delivery (published nightly, Cinnamon X11)

`xinput test "AT Translated Set 2 keyboard"` while QMP sent `menu`, then `compose`:

    key press   135
    key release 135

Only `compose` reached the X server. QMP `menu` produced no X event, no Qt event and no popup,
on Cinnamon and on GNOME. QEMU's keycode table maps qcode `menu` to Linux KEY_MENU with no AT
set 2 code, and the lab guests use the PS/2 keyboard. The Menu key on a keyboard is KEY_COMPOSE.

## Real Menu key, published nightly (same order on Cinnamon and GNOME)

    QListView(historyList) ContextMenu reason=1 pos=325,53 global=557,221
    QMenu(historyRowMenu) MenuShow popup=null
    QAction() Shortcut seq=Menu popup=QMenu(historyRowMenu)
    QMenu(historyRowMenu) MenuShow popup=QMenu(historyRowMenu)

Two row menus stack. After one Esc on Cinnamon: 2 MenuShow, 1 MenuHide, one menu still open.

## Real Menu key, fixed build

| Check | Cinnamon X11 | GNOME Wayland |
| --- | --- | --- |
| MenuShow for one key press | 1 | 1 |
| Selected ID before the key | f1379078-fab2-4505-8c6e-67c43e398a2b | operation:c582489a-69dd-4aa1-8f6c-af12d92e1b70 |
| `id` in clipboard after a real click on Copy details | f1379078-fab2-4505-8c6e-67c43e398a2b | operation:c582489a-69dd-4aa1-8f6c-af12d92e1b70 |
| One Esc | 1 MenuHide, closed | 1 MenuHide, closed |
| Shift+F10 | 1 MenuShow | 1 MenuShow |

The Menu shortcut still fires while the menu is open; the guard makes it a no-op.

## Offscreen regression test

`realMenuKeyOpensOneRowMenuForTheSelectedRow` fails before the fix on Qt 6.8.2 (peak 2, expected 1)
and passes after it. With the fix, the whole `gui_history_view` suite passes on Qt 6.4.2 and 6.10.2.
