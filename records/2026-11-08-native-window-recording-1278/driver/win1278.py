#!/usr/bin/env python3
"""#1278 acceptance test window (GTK 3): a ball bouncing at 30 fps on a dark
field with a moving bar, or a still pattern (--still). Commands on stdin, one
per line: resize W H | maximize | unmaximize | iconify | present | quit.
Prints `mapped` once the window is shown."""
import argparse, math, sys, time
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GLib, Gtk

p = argparse.ArgumentParser()
p.add_argument('--title', required=True)
p.add_argument('--still', action='store_true')
p.add_argument('--size', default='640x480')
p.add_argument('--color', default='0.10,0.10,0.30')
args = p.parse_args()
w0, h0 = (int(v) for v in args.size.split('x'))
bg = [float(v) for v in args.color.split(',')]
t0 = time.monotonic()
window = Gtk.Window(title=args.title)
window.set_default_size(w0, h0)
area = Gtk.DrawingArea()
window.add(area)


def draw(widget, cr):
    a = widget.get_allocation()
    t = 0 if args.still else time.monotonic() - t0
    cr.set_source_rgb(*bg)
    cr.paint()
    # A fixed grid so a still window is not uniform.
    cr.set_source_rgb(0.35, 0.35, 0.45)
    for x in range(0, a.width, 80):
        cr.rectangle(x, 0, 2, a.height)
    for y in range(0, a.height, 80):
        cr.rectangle(0, y, a.width, 2)
    cr.fill()
    x = (math.sin(t * 2.1) * 0.42 + 0.5) * a.width
    y = (math.cos(t * 1.3) * 0.42 + 0.5) * a.height
    cr.set_source_rgb(1, 0.85, 0.1)
    cr.arc(x, y, 36, 0, 2 * math.pi)
    cr.fill()
    cr.set_source_rgb(1, 1, 1)
    cr.rectangle(0, 0, a.width * ((t % 3) / 3), 14)
    cr.fill()


area.connect('draw', draw)
if not args.still:
    GLib.timeout_add(33, lambda: (area.queue_draw(), True)[1])


def command(channel, _condition):
    line = channel.readline()
    if not line:
        Gtk.main_quit()
        return False
    words = line.split()
    if not words:
        return True
    if words[0] == 'resize':
        window.resize(int(words[1]), int(words[2]))
    elif words[0] == 'maximize':
        window.maximize()
    elif words[0] == 'unmaximize':
        window.unmaximize()
    elif words[0] == 'iconify':
        window.iconify()
    elif words[0] == 'present':
        window.present()
    elif words[0] == 'quit':
        Gtk.main_quit()
        return False
    print('done', words[0], flush=True)
    return True


GLib.io_add_watch(GLib.IOChannel.unix_new(sys.stdin.fileno()), GLib.IO_IN | GLib.IO_HUP, command)
window.connect('destroy', Gtk.main_quit)
window.connect('map-event', lambda *_: print('mapped', flush=True))
window.show_all()
window.present()
Gtk.main()
