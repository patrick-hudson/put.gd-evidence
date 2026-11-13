#!/usr/bin/env python3
import gi,json,sys
from pathlib import Path
gi.require_version('Gtk','3.0')
from gi.repository import Gtk,GLib
out=Path(sys.argv[1]); win=Gtk.Window(title='Sweep synthetic scroll page'); win.set_default_size(800,600)
scroll=Gtk.ScrolledWindow(); area=Gtk.DrawingArea(); area.set_size_request(760,2600)
def draw(widget,c):
 c.set_source_rgb(1,1,1); c.paint(); c.select_font_face('Sans'); c.set_font_size(18)
 for i in range(100):
  y=i*26; c.set_source_rgb((i*37%255)/255,(i*71%255)/255,(i*13%255)/255); c.rectangle(0,y,760,24); c.fill(); c.set_source_rgb(0,0,0); c.move_to(30,y+19); c.show_text('Synthetic line %03d -- acceptance only'%i)
area.connect('draw',draw); scroll.add(area); win.add(scroll); win.connect('destroy',Gtk.main_quit); win.show_all()
def ready():
 origin=scroll.get_window().get_origin(); allocation=scroll.get_allocation(); (out/'scroll-rect.json').write_text(json.dumps({'rect':[origin[-2]+3,origin[-1]+3,allocation.width-6,allocation.height-6]})); return False
GLib.timeout_add(500,ready); Gtk.main()
