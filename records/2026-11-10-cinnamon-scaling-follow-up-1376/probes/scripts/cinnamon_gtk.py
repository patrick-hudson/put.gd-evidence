import os,json
os.environ.update(GTK_A11Y='none',NO_AT_BRIDGE='1')
import gi
gi.require_version('Gtk','3.0');from gi.repository import Gtk,GLib,Gdk
w=Gtk.Window(title='Cinnamon scale witness GTK3');w.set_default_size(500,250)
l=Gtk.Label(label='GTK scale witness: 100 logical pixels below\n'+'█'*10);w.add(l);w.show_all()
def report():
 d={'scale_factor':w.get_scale_factor(),'allocated':[w.get_allocated_width(),w.get_allocated_height()],'gdk_dpi':Gdk.Screen.get_default().get_resolution()};print(json.dumps(d),flush=True);return True
GLib.timeout_add(1000,report);Gtk.main()
