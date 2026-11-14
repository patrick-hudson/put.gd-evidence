#!/usr/bin/env python3
"""Extend the native GTK clipboard witness with motion, PRIMARY and a real button."""
import sys,json,math,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'tools/lab'))
sys.path.insert(0,str(Path(__file__).parent))
from gtk_clipboard_fixture import Fixture,Gdk,Gtk,GLib,write_json,cairo
class SweepFixture(Fixture):
 def __init__(self,out):
  super().__init__(out);self.motion=False;self.phase=0;self.clicks=0
 def activate_fixture(self,app):
  super().activate_fixture(app)
  drawing=self.window.get_child(); gesture=Gtk.GestureClick.new();gesture.connect('pressed',self.clicked);drawing.add_controller(gesture)
  GLib.timeout_add(50,self.tick)
  s=cairo.ImageSurface(cairo.FORMAT_RGB24,900,180);c=cairo.Context(s);c.set_source_rgb(1,1,1);c.paint();c.set_source_rgb(0,0,0);c.select_font_face('Sans');c.set_font_size(32);c.move_to(20,70);c.show_text('putgd B acceptance text');s.write_to_png(str(self.output/'text.png'))
 def clicked(self,_gesture,_count,x,y):
  if 40<=x<=220 and 340<=y<=395:
   self.clicks+=1;write_json(self.output/'clicks.json',{'count':self.clicks,'x':x,'y':y,'at':time.monotonic()});self.window.get_child().queue_draw()
 def paint(self,drawing,c,width,height):
  if not self.motion:super().paint(drawing,c,width,height)
  else:
   colors=[(.86,.12,.16),(.08,.7,.27),(.14,.27,.86),(.92,.74,.08)]
   for y in range(0,height,128):
    for x in range(-128,width+128,32):
     c.set_source_rgb(*colors[(x//32)%4]);c.rectangle(x+self.phase%128,y,32,128);c.fill()
    for x in range(0,width,128):
     c.set_source_rgb(1,1,1);c.arc(x+64+35*math.sin(self.phase/18),y+64+35*math.cos(self.phase/18),10,0,2*math.pi);c.fill()
  c.set_source_rgb(.8,.8,.8);c.rectangle(40,340,180,55);c.fill();c.set_source_rgb(0,0,0);c.select_font_face('Sans');c.set_font_size(18);c.move_to(55,375);c.show_text('Clicks: %d'%self.clicks)
 def tick(self):
  p=self.output/'control.json'
  if p.exists():
   value=json.loads(p.read_text());p.unlink()
   if 'motion' in value:self.motion=value['motion'];self.window.get_child().queue_draw()
   if value.get('primarySet'):
    self.window.get_display().get_primary_clipboard().set_content(Gdk.ContentProvider.new_for_bytes('text/plain;charset=utf-8',GLib.Bytes.new(b'putgd B PRIMARY sentinel')))
   if value.get('primaryRead'):
    cb=self.window.get_display().get_primary_clipboard()
    def got(owner,result):
     try:write_json(self.output/'primary.json',{'text':owner.read_text_finish(result)})
     except Exception as e:write_json(self.output/'primary.json',{'error':type(e).__name__})
    cb.read_text_async(None,got)
   write_json(self.output/'control-ack.json',{'id':value.get('id'),'at':time.monotonic()})
  if self.motion:self.phase+=5;self.window.get_child().queue_draw()
  return True
SweepFixture(Path(sys.argv[1])).run([])
