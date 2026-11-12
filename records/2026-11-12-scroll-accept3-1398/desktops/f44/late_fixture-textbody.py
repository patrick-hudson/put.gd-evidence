# Deterministic full-pixel generator for late bars and a bottom live counter.
import sys,json,signal
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from PyQt6.QtWidgets import QApplication,QWidget,QScrollArea
from PyQt6.QtGui import QPainter,QImage,QColor
from PyQt6.QtCore import Qt
P=Path('/home/patrick/work/s3a');mode=sys.argv[1];W=960;H=24000;step=[0]
im=Image.new('RGB',(W,H),'white');d=ImageDraw.Draw(im);font=ImageFont.truetype(str(next(Path('/usr/share/fonts').rglob('DejaVuSansMono.ttf'))),16)
for y in range(0,H,24):d.text((16,y),f'Body row {y//24:04d} independent exact oracle',font=font,fill='black')
im.save(P/(mode+'-generator.png'))
class Page(QWidget):
 def __init__(self):
  super().__init__();self.setFixedSize(W,H+36 if mode in ['counter','late'] else H);self.pic=QImage(str(P/(mode+'-generator.png')))
 def paintEvent(self,e):
  q=QPainter(self);q.drawImage(0,0,self.pic)
class Band(QWidget):
 def __init__(self,parent,top=False):super().__init__(parent);self.top=top;self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
 def paintEvent(self,e):
  pic=Image.new('RGB',(W,36),'#205080' if self.top else '#806020');z=ImageDraw.Draw(pic);z.text((15,5),'Late top bar' if self.top else ('Counter '+str(step[0]) if mode=='counter' else 'Late bottom banner'),font=font,fill='white');fn=P/(mode+('-top.png' if self.top else '-footer.png'));pic.save(fn);q=QPainter(self);q.drawImage(0,0,QImage(str(fn)))

a=QApplication([]);w=QWidget();w.setStyleSheet('background:#666');s=QScrollArea(w);s.setGeometry(100,200,W,600);s.setFrameShape(QScrollArea.Shape.NoFrame);s.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff);s.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff);page=Page();s.setWidget(page);top=Band(w,True);top.setGeometry(100,200,W,36);top.hide();bottom=Band(w);bottom.setGeometry(100,764,W,36);bottom.setVisible(mode=='counter')
def changed(pos):
 step[0]=0 if pos==0 else step[0]+1
 if mode=='late':top.setVisible(pos>300);bottom.setVisible(step[0]>=2)
 if mode=='nonfixed':
  if pos==0:changed.active=True;changed.maximum=0
  if getattr(changed,'active',False) and pos>changed.maximum:
   changed.maximum=pos;y=pos+552
   if y<H:
    d.rectangle((0,y,W-1,min(H-1,y+35)),fill='#806020');d.text((15,y+5),'Nonfixed counter '+str(step[0]),font=font,fill='white');raw=im.tobytes();page.pic=QImage(raw,W,H,W*3,QImage.Format.Format_RGB888).copy();page.update()

 bottom.update();print(json.dumps({'pos':pos,'step':step[0],'top':top.isVisible(),'bottom':bottom.isVisible()}),flush=True)
signal.signal(signal.SIGTERM,lambda *_:(im.save(P/(mode+'-generator.png')),a.quit()));s.verticalScrollBar().valueChanged.connect(changed);s.verticalScrollBar().setValue(H+36-600);w.showFullScreen();a.exec()
