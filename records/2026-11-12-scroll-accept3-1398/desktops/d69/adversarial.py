import sys,os,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
P=Path('/home/patrick/work/s3a');kind=sys.argv[1];W=960;H=24000
im=Image.new('RGB',(W,H),'white');d=ImageDraw.Draw(im);font=ImageFont.truetype(str(next(Path('/usr/share/fonts').rglob('DejaVuSansMono.ttf'))),16)
if kind=='a':
 for y in range(0,H,24):d.text((16,y),f'Identical table record 0000000000000000000000000000000000000000 {y//24:04d}',font=font,fill='black')
elif kind=='b':
 for y in range(0,H,48):
  t='ABCD EFGH IJKL MNOP' if (y//48)%2 else 'PONM LKJI HGFE DCBA'
  d.text((32,y),t,font=font,fill='black');d.text((32,y+24),t[::-1],font=font,fill='black')
elif kind=='c':
 for y in range(0,H,138):
  d.rectangle((10,y+2,950,y+135),fill='#eeeeee');d.text((30,y+20),'ODD BLOCK' if (y//138)%7==6 else 'REPEATING BLOCK',font=font,fill='black')
if kind=='f':
 d.rectangle((0,0,287,H),fill='#334455');d.rectangle((672,0,959,H),fill='#554433')
 for y in range(0,H,24):d.text((296,y),f'Centre record {y//24:04d}',font=font,fill='black')
im.save(P/(kind+'-generator.png'))
from PyQt6.QtWidgets import QApplication,QWidget,QScrollArea
from PyQt6.QtGui import QPainter,QImage
from PyQt6.QtCore import Qt
class Page(QWidget):
 def __init__(self):
  super().__init__();self.setFixedSize(W,H);self.pic=QImage(str(P/(kind+'-generator.png')))
 def paintEvent(self,e):
  q=QPainter(self);q.drawImage(0,0,self.pic)
a=QApplication([]);w=QWidget();w.setStyleSheet('background:#666');s=QScrollArea(w);s.setGeometry(100,200,W,600);s.setFrameShape(QScrollArea.Shape.NoFrame);s.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff);s.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff);s.setWidget(Page());s.verticalScrollBar().setValue(H-600);s.verticalScrollBar().valueChanged.connect(lambda x:print('position',x,flush=True));w.showFullScreen();
from PyQt6.QtCore import QTimer
QTimer.singleShot(100,lambda:print(json.dumps({"ready":True,"pos":s.verticalScrollBar().value(),"maximum":s.verticalScrollBar().maximum(),"platform":a.platformName()}),flush=True));a.exec()
