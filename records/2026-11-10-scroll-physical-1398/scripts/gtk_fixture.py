import gi,sys
gi.require_version('Gtk','4.0')
from gi.repository import Gtk,Gio
class App(Gtk.Application):
 def __init__(self):super().__init__(application_id="gd.put.ScrollAcceptance",flags=Gio.ApplicationFlags.NON_UNIQUE)
 def do_activate(self):
  w=Gtk.ApplicationWindow(application=self,title='put.gd acceptance GTK ruler');fixed=Gtk.Fixed();w.set_child(fixed)
  s=Gtk.ScrolledWindow();s.set_policy(Gtk.PolicyType.EXTERNAL,Gtk.PolicyType.EXTERNAL);s.set_size_request(960,600);fixed.put(s,100,100)
  d=Gtk.DrawingArea();d.set_content_width(960);d.set_content_height(2400);s.set_child(d)
  def draw(a,c,width,height):
   c.set_source_rgb(250/255,250/255,250/255);c.paint();c.set_source_rgb(16/255,16/255,16/255)
   _,top,_,bottom=c.clip_extents()
   for r in range(max(0,int(top)//40),min(60,int(bottom)//40+1)):
    c.move_to(4,r*40+20);c.show_text(str(r))
    for l in range(40):
     if l<2:b=65535
     elif l<30:b=r
     else:
      x=(r*2654435761+l*40503+0x9e3779b9)&0xffffffff;x^=x>>15;x=x*0x2c1b3c6d&0xffffffff;x^=x>>12;x=x*0x297a2d39&0xffffffff;x^=x>>15;b=x&65535;b=b if b not in (0,65535) else 0x5a5a^l
     for col in range(16):
      if b&(0x8000>>col):c.rectangle(64+col*55,r*40+l,55,1)
    c.fill()
  d.set_draw_func(draw);w.fullscreen();w.present()
App().run([sys.argv[0]])
