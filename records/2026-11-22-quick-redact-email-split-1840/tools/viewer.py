"""A compositor-native fullscreen window showing one synthetic fixture PNG at 1:1 from (0, 0)."""
import json, sys
from pathlib import Path
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, Gdk, GdkPixbuf

control = Path(sys.argv[1])
window = Gtk.Window(title='put.gd synthetic fixture viewer')
window.connect('destroy', Gtk.main_quit)
image = Gtk.Image()
image.set_halign(Gtk.Align.START); image.set_valign(Gtk.Align.START)
window.add(image)
css = Gtk.CssProvider(); css.load_from_data(b'window { background: #303030; }')
Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
state = {'stamp': None, 'full': None}

def refresh():
    try:
        want = json.loads(control.read_text())
    except (OSError, ValueError):
        return True
    stamp = (want.get('path'), want.get('n'))
    if stamp != state['stamp']:
        state['stamp'] = stamp
        if want.get('path'):
            image.set_from_pixbuf(GdkPixbuf.Pixbuf.new_from_file(want['path']))
            window.show_all(); window.present()
        else:
            window.hide()
    if want.get('fullscreen') != state['full']:
        state['full'] = want.get('fullscreen')
        window.fullscreen() if state['full'] else window.unfullscreen()
    return True

refresh()
GLib.timeout_add(100, refresh)
Gtk.main()
