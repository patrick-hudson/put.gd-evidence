#!/usr/bin/env python3
import gi,json,sys,pathlib
gi.require_version('Gtk','3.0')
from gi.repository import Gtk,GLib
out=pathlib.Path(sys.argv[1]); win=Gtk.Window(title='Sweep synthetic menu fixture'); win.set_default_size(500,350)
box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL); bar=Gtk.MenuBar(); item=Gtk.MenuItem(label='Synthetic menu'); menu=Gtk.Menu()
for name in ('Synthetic item one','Synthetic item two','Synthetic item three'): menu.append(Gtk.MenuItem(label=name))
item.set_submenu(menu); bar.append(item); box.pack_start(bar,False,False,0); box.pack_start(Gtk.Label(label='Only synthetic lab content'),True,True,0); win.add(box); win.connect('destroy',Gtk.main_quit); win.show_all()
def ready():
 origin=item.get_window().get_origin(); a=item.get_allocation(); (out/'menu-point.json').write_text(json.dumps([origin[-2]+a.x+a.width//2,origin[-1]+a.y+a.height//2])); return False
GLib.timeout_add(500,ready); Gtk.main()
