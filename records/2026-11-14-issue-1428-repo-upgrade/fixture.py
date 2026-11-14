import gi
gi.require_version("Gtk","3.0")
from gi.repository import Gtk,Gdk
w=Gtk.Window(title="put.gd repository upgrade fixture")
w.fullscreen()
a=Gtk.DrawingArea()
def draw(a,c):
 c.set_source_rgb(1,1,1);c.paint();c.set_source_rgb(0,0,0);c.select_font_face("DejaVu Sans");c.set_font_size(24)
 for i,s in enumerate(["Repository upgrade test", "English text is ready", "Copy this region"]):
  c.move_to(140,180+i*40);c.show_text(s)
a.connect("draw",draw);w.add(a);w.show_all();Gtk.main()
