import sys, argparse,os
OFFSET=int(os.environ.get("SC_Y","100"))
z=argparse.ArgumentParser();z.add_argument("--rows",type=int,default=60);z.add_argument("--start",type=int,default=0);z.add_argument("--sticky",action="store_true");opts=z.parse_args()
from PyQt6.QtWidgets import QApplication,QWidget,QScrollArea,QVBoxLayout
from PyQt6.QtGui import QPainter,QColor
from PyQt6.QtCore import Qt
class Page(QWidget):
 def __init__(self):super().__init__();self.setFixedSize(960,opts.rows*40)
 def paintEvent(self,e):
  p=QPainter(self);p.fillRect(self.rect(),QColor('#fafafa'));p.setPen(QColor('#101010'))
  for r in range(max(0,e.rect().top()//40),min(opts.rows,e.rect().bottom()//40+1)):
   p.drawText(4,r*40+20,str(r))
   for l in range(40):
    if l<2:b=65535
    elif l<30:b=r
    else:
     x=(r*2654435761+l*40503+0x9e3779b9)&0xffffffff;x^=x>>15;x=x*0x2c1b3c6d&0xffffffff;x^=x>>12;x=x*0x297a2d39&0xffffffff;x^=x>>15;b=x&65535;b=b if b not in (0,65535) else 0x5a5a^l
    for c in range(16):
     if b&(0x8000>>c):p.fillRect(64+c*55,r*40+l,55,1,QColor('#101010'))
a=QApplication(sys.argv);w=QWidget();w.setWindowTitle('put.gd acceptance Qt ruler');w.setStyleSheet('background:#666');s=QScrollArea(w);s.setGeometry(100,OFFSET+40 if opts.sticky else OFFSET,960,520 if opts.sticky else 600);s.setFrameShape(QScrollArea.Shape.NoFrame);s.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff);s.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff);s.setWidget(Page());s.verticalScrollBar().setValue(opts.start)
if opts.sticky:
 for y,color in ((OFFSET,"#205080"),(OFFSET+560,"#806020")):
  band=QWidget(w);band.setGeometry(100,y,960,40);band.setStyleSheet("background:"+color)
w.showFullScreen();sys.exit(a.exec())
