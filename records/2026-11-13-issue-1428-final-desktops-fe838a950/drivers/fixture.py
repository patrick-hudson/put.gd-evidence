import gi,cairo,os
gi.require_version('Gtk','3.0')
from gi.repository import Gtk,GLib
from pathlib import Path
base=Path(__file__).parent
w=Gtk.Window(title='Synthetic acceptance text 1428');w.fullscreen();a=Gtk.DrawingArea();w.add(a)
def text(c,x,y):
 c.set_source_rgb(0,0,0);c.select_font_face('DejaVu Sans',0,0);c.set_font_size(32)
 for i,line in enumerate(['ALPHA BRAVO CHARLIE','SYNTHETIC TEXT 1428','hello@example.test']): c.move_to(x,y+i*48);c.show_text(line)
def draw(a,c):
 width=a.get_allocated_width();height=a.get_allocated_height();c.set_source_rgb(1,1,1);c.paint()
 if (base/'mode').exists() and (base/'mode').read_text().strip()=='qr':
  s=cairo.ImageSurface.create_from_png(str(base/'qr.png'));c.set_source_surface(s,(width-s.get_width())/2,(height-s.get_height())/2);c.paint()
 else:text(c,(width-600)/2,height/2-45)
a.connect('draw',draw);GLib.timeout_add(200,lambda:(a.queue_draw() or True));w.connect('destroy',Gtk.main_quit)
s=cairo.ImageSurface(cairo.FORMAT_RGB24,800,300);c=cairo.Context(s);c.set_source_rgb(1,1,1);c.paint();text(c,70,80);s.write_to_png(str(base/'text.png'));w.show_all();Gtk.main()
