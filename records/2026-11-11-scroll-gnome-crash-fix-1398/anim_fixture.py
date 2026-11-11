# A full-screen Qt window with a bar that moves every frame: something for a recording to show.
import sys
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtCore import QTimer
class Page(QWidget):
    def __init__(self):
        super().__init__(); self.t = 0
        self.timer = QTimer(self); self.timer.timeout.connect(self.step); self.timer.start(33)
    def step(self):
        self.t += 1; self.update()
    def paintEvent(self, e):
        p = QPainter(self); p.fillRect(self.rect(), QColor('#303840'))
        x = 100 + (self.t * 12) % 900
        p.fillRect(x, 200, 60, 600, QColor('#f0c040')); p.end()
a = QApplication(sys.argv); w = Page(); w.setWindowTitle('put.gd fx5 moving bar'); w.showFullScreen(); print('ready', flush=True); sys.exit(a.exec())
