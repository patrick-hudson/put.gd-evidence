#!/usr/bin/env python3
"""Owned GTK X11 long page plus a second independent key receiver. No grabs."""
import gi
gi.require_version('Gtk','3.0')
from gi.repository import Gtk,Gdk,GLib
import json,time,pathlib,sys
root=pathlib.Path(sys.argv[1]);root.mkdir(exist_ok=True);pos=0;total=12000;wheels=0;serial=0
def event(kind,**data):
 with (root/'events.jsonl').open('a') as f:f.write(json.dumps({'monotonic':time.monotonic(),'wallTime':time.time(),'kind':kind,**data})+'\n')
def state():
 p=root/'state.tmp';p.write_text(json.dumps({'position':pos,'total':total,'wheels':wheels}));p.replace(root/'state.json')
page=Gtk.Window(title='Sweep C scrolling page');page.set_decorated(False);page.set_default_size(640,500);page.move(160,150)
area=Gtk.DrawingArea();area.set_can_focus(True);area.add_events(Gdk.EventMask.SCROLL_MASK|Gdk.EventMask.SMOOTH_SCROLL_MASK);page.add(area)
def draw(widget,cr):
 width=widget.get_allocated_width();height=widget.get_allocated_height();cr.set_source_rgb(.94,.94,.94);cr.paint()
 for y in range(height):
  row=pos+y;bits=((row//8+1)*2654435761)^((row%8)*2246822519);cr.set_source_rgb(.10,.18,.27)
  for bit in range(16):
   if bits&(1<<bit):cr.rectangle(80+bit*32,y,31,1)
 cr.fill();cr.set_source_rgb(.1,.1,.1);cr.select_font_face('monospace');cr.set_font_size(13)
 for row in range(pos//32*32,pos+height,32):cr.move_to(5,row-pos+15);cr.show_text(str(row//32))
 thumb=max(24,int(height*height/total));top=int(pos*(height-thumb)/max(1,total-height));cr.set_source_rgb(.75,.75,.75);cr.rectangle(width-18,0,18,height);cr.fill();cr.set_source_rgb(.3,.3,.3);cr.rectangle(width-16,top,14,thumb);cr.fill();return False
def scroll(widget,e):
 global pos,wheels
 direction=1 if e.direction==Gdk.ScrollDirection.DOWN else -1 if e.direction==Gdk.ScrollDirection.UP else (1 if e.delta_y>0 else -1)
 wheels+=1;pos=max(0,min(total-area.get_allocated_height(),pos+direction*100));event('wheel',direction=direction,position=pos,count=wheels);state();area.queue_draw();return True
area.connect('draw',draw);area.connect('scroll-event',scroll)
other=Gtk.Window(title='Sweep C other key receiver');other.set_default_size(430,180);other.move(1080,250);label=Gtk.Label(label='Owned key receiver\nEscape events are logged; no key is grabbed.');other.add(label)
def key(win,e,name):event('key-press',window=name,key=Gdk.keyval_name(e.keyval),hardwareKeycode=e.hardware_keycode);return False
page.connect('key-press-event',key,'page');other.connect('key-press-event',key,'other')
for win in (page,other):win.connect('destroy',lambda w:Gtk.main_quit());win.show_all()
def tick():
 global serial,pos,total
 p=root/'control.json'
 if p.exists():
  j=json.loads(p.read_text())
  if j['serial']!=serial:
   serial=j['serial'];total=j.get('total',12000);pos=0;state();area.queue_draw();event('reset',serial=serial,total=total)
 if area.get_window():
  origin=area.get_window().get_origin();(root/'geometry.json').write_text(json.dumps({'x':origin.x,'y':origin.y,'width':area.get_allocated_width(),'height':area.get_allocated_height()}))
 return True
state();GLib.timeout_add(50,tick);Gtk.main()
