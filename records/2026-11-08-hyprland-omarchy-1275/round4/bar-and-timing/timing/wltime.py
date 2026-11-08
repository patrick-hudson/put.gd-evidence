#!/usr/bin/env python3
"""wltime.py TRIALS.jsonl WAYLAND_DEBUG.log: per trial, when (seconds after the hotkey, guest clock) the resident saw and did each catcher step."""
import json, re, sys
rows = [json.loads(l) for l in open(sys.argv[1])]
stamp = re.compile(r'^\[(\d\d):(\d\d):(\d\d\.\d+)\]\s+(?:\{[^}]*\}\s+)?(.*)')
lines = []
for raw in open(sys.argv[2], errors='replace'):
    m = stamp.match(raw)
    if m: lines.append((int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3)), m.group(4)))
print(json.dumps({'lines': len(lines), 'first': lines[0] if lines else None}))
def window(row):
    base = row['hotkeyGuest'] % 86400
    return [(round((t - base) * 1000, 1), text) for t, text in lines if -0.2 <= t - base <= 4.0]
def first(evts, pat):
    for d, t in evts:
        if re.search(pat, t): return d, t
    return None, None
for row in rows:
    ev = window(row)
    _, ls = first(ev, r'get_layer_surface.*putgd-region-catcher')
    pressed_t, pressed_line = first(ev, r'hyprland_global_shortcut_v1#\d+\.pressed')
    sent_t, _ = first(ev, r'get_layer_surface.*putgd-region-catcher')
    surf = None
    if ls:
        m = re.search(r'new id zwlr_layer_surface_v1#(\d+), wl_surface#(\d+)', ls)
        if m: surf = m.group(2); lay = m.group(1)
    conf_t = commit_t = enter_t = button_t = motion_t = None
    if surf:
        conf_t, _ = first(ev, r'zwlr_layer_surface_v1#%s\.configure' % lay)
        for d, t in ev:
            if conf_t is not None and d >= conf_t and re.search(r'wl_surface#%s\.commit' % surf, t): commit_t = d; break
        enter_t, _ = first(ev, r'wl_pointer#\d+\.enter\(\d+, wl_surface#%s,' % surf)
    # any catcher surface (more than one output): first enter/button after creation
    ids = re.findall(r'new id zwlr_layer_surface_v1#\d+, wl_surface#(\d+)', '\n'.join(t for d, t in ev if 'putgd-region-catcher' in t))
    if ids:
        pat = '|'.join(ids); enter_any, _ = first(ev, r'wl_pointer#\d+\.enter\(\d+, wl_surface#(%s),' % pat)
        button_t, _ = first(ev, r'wl_pointer#\d+\.button\(')
        if button_t is not None and sent_t is not None and button_t < sent_t: button_t = None
    else: enter_any = None
    out = {'trial': row['trial'], 'outcome': row['outcome'], 'pressedEventMs': pressed_t, 'layerRequestMs': sent_t, 'configureMs': conf_t, 'bufferCommitMs': commit_t, 'enterOnCatcherMs': enter_any, 'buttonSeenMs': button_t, 'pressInjectedMs': round((row['pressGuest'] - row['hotkeyGuest']) * 1000, 1), 'catcherSeenMs': row['catcherSeen'] and round(row['catcherSeen'] * 1000), 'surfaces': len(ids), 'pressedLine': pressed_line and pressed_line[:110], 'load1': row.get('load1')}
    print(json.dumps(out))
