# The acceptance round's native Qt ruler (PyQt6), with SC_SLOW=<ms> to make
# every repaint take that long (the slow-painting page).
import sys, argparse, os, time
OFFSET = int(os.environ.get("SC_Y", "100"))
SLOW = int(os.environ.get("SC_SLOW", "0"))
z = argparse.ArgumentParser(); z.add_argument("--rows", type=int, default=60); z.add_argument("--start", type=int, default=0); z.add_argument("--sticky", action="store_true"); opts = z.parse_args()
from PyQt6.QtWidgets import QApplication, QWidget, QScrollArea
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtCore import Qt
class Page(QWidget):
    def __init__(self):
        super().__init__(); self.setFixedSize(1900, opts.rows * 40)
    def paintEvent(self, e):
        t0 = time.monotonic()
        if SLOW: time.sleep(SLOW / 1000)
        p = QPainter(self); p.fillRect(self.rect(), QColor('#fafafa')); p.setPen(QColor('#101010'))
        for r in range(max(0, e.rect().top() // 40), min(opts.rows, e.rect().bottom() // 40 + 1)):
            p.drawText(4, r * 40 + 20, str(r))
            for l in range(40):
                if l < 2: b = 65535
                elif l < 30: b = r
                else:
                    x = (r * 2654435761 + l * 40503 + 0x9e3779b9) & 0xffffffff; x ^= x >> 15; x = x * 0x2c1b3c6d & 0xffffffff; x ^= x >> 12; x = x * 0x297a2d39 & 0xffffffff; x ^= x >> 15; b = x & 65535; b = b if b not in (0, 65535) else 0x5a5a ^ l
                for c in range(16):
                    if b & (0x8000 >> c): p.fillRect(64 + c * 55, r * 40 + l, 55, 1, QColor('#101010'))
        p.end(); print('painted %d-%d %.3f %.3f' % (e.rect().top(), e.rect().bottom(), t0, time.monotonic()), flush=True)
a = QApplication(sys.argv); w = QWidget(); w.setWindowTitle('put.gd sf1398 Qt ruler'); w.setStyleSheet('background:#666')
s = QScrollArea(w); s.setGeometry(0,0,1900,1080); s.setFrameShape(QScrollArea.Shape.NoFrame)
s.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff); s.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff); s.setWidget(Page()); s.verticalScrollBar().setValue(opts.start)
s.verticalScrollBar().valueChanged.connect(lambda v: print("position %d %.3f" % (v, time.monotonic()), flush=True))
if opts.sticky:
    for y, color in ((OFFSET, "#205080"), (OFFSET + 560, "#806020")):
        band = QWidget(w); band.setGeometry(100, y, 960, 40); band.setStyleSheet("background:" + color)
BLINK = int(os.environ.get("SC_BLINK", "0"))
if BLINK:
    # Constant damage outside the captured rectangle: a small square that changes colour.
    from PyQt6.QtCore import QTimer
    dot = QWidget(w); dot.setGeometry(1500, 900, 6, 6); state = [0]
    def tick():
        state[0] ^= 1; dot.setStyleSheet('background:#%s' % ('707070' if state[0] else '606060'))
    timer = QTimer(); timer.timeout.connect(tick); timer.start(BLINK)
w.showFullScreen(); print("ready", flush=True); sys.exit(a.exec())
