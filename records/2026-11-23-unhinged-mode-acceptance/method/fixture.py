import gi, sys, time
from pathlib import Path
gi.require_version('Gtk','3.0')
gi.require_version('GdkPixbuf','2.0')
from gi.repository import Gtk,Gdk,GdkPixbuf,GLib
root=Path(sys.argv[1])
cover=Gtk.Window(title='s1937acc — Synthetic OCR fixture')
cover.set_decorated(False)
area=Gtk.DrawingArea()
cover.add(area)
tokens=GdkPixbuf.Pixbuf.new_from_file(str(root/'tokens.png'))
mode='cover'
size=(0,0)
scaled=None
def draw(widget, ctx):
    global scaled,size
    ctx.set_source_rgb(1,0,1)
    ctx.paint()
    if mode != 'cover':
        w,h=area.get_allocated_width(),area.get_allocated_height()
        if size!=(w-16,h-16):
            size=w-16,h-16
            scaled=tokens.scale_simple(*size,GdkPixbuf.InterpType.BILINEAR)
        Gdk.cairo_set_source_pixbuf(ctx,scaled,8,8)
        ctx.paint()
    return False
area.connect('draw',draw)
cover.show_all()
cover.fullscreen_on_monitor(cover.get_screen(),0)
pad=Gtk.Window(title='s1937acc — Input timing')
pad.set_default_size(550,80)
pad.set_transient_for(cover)
entry=Gtk.Entry()
pad.add(entry)
log=None
def changed(widget):
    if log:
        print(f'{time.monotonic():.9f},{entry.get_text()}',file=log,flush=True)
entry.connect('changed',changed)
seen=''
def step():
    global mode,seen,log
    value=(root/'fixture-mode').read_text()
    if value==seen:
        if value.startswith('input-') and pad.is_active() and entry.has_focus():
            (root/f'{value}.focused').touch()
        return True
    seen=value
    if value.startswith('input-'):
        if log: log.close()
        log=None
        entry.set_text('')
        log=(root/f'{value}.csv').open('w')
        print('monotonic_s,entry',file=log,flush=True)
        pad.show_all()
        pad.present()
        entry.grab_focus()
    elif value=='exit':
        Gtk.main_quit()
    else:
        pad.hide()
        mode=value
        area.queue_draw()
    return True
GLib.timeout_add(10,step)
Gtk.main()
