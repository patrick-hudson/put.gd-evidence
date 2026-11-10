#include "editor/EditorCanvas.h"
#include <QApplication>
#include <QElapsedTimer>
#include <cstdio>
#include <numeric>
#include <algorithm>
using namespace putgd::editor;
class Canvas:public EditorCanvas{public:using EditorCanvas::EditorCanvas;std::vector<double> times;protected:void paintEvent(QPaintEvent* event)override{QElapsedTimer t;t.start();EditorCanvas::paintEvent(event);times.push_back(t.nsecsElapsed()/1e6);}};
int main(int argc,char**argv){QApplication app(argc,argv);std::puts("build,width,height,mask,interaction,samples,mean_ms,worst_ms");
 for(QSize size:{QSize(3840,2160),QSize(6000,4000)})for(int kind=0;kind<3;++kind)for(int interaction=0;interaction<(kind?3:1);++interaction){
  QImage source(size,QImage::Format_RGB32);source.fill(QColor(240,80,210));EditDocument doc(source);Shape mask;mask.kind=Shape::Kind::Redact;mask.rect=kind==1?QRect(100,100,600,50):QRect(100,100,size.width()-200,size.height()-200);const auto initial=mask.rect;
  if(kind)mask.id=doc.add(mask);
  Canvas canvas(doc);canvas.resize(1200,800);canvas.fit();QImage output(canvas.size(),QImage::Format_RGB32);
  for(int i=0;i<20;++i)canvas.render(&output);canvas.times.clear();
  for(int i=0;i<300;++i){
   if(interaction==1){mask.rect=initial.translated((size.width()-initial.width()-initial.x())*i/299,(size.height()-initial.height()-initial.y())*i/299);doc.preview(mask);}
   if(interaction==2){mask.rect=QRect(initial.topLeft(),QSize(initial.width()+(size.width()-initial.width()-initial.x())*i/299,initial.height()+(size.height()-initial.height()-initial.y())*i/299));doc.preview(mask);}
   canvas.render(&output);
  }
  auto& t=canvas.times;std::printf("%s,%d,%d,%s,%s,%zu,%.4f,%.4f\n",argv[1],size.width(),size.height(),kind==0?"none":kind==1?"small":"large",interaction==0?"still":interaction==1?"drag":"resize",t.size(),std::accumulate(t.begin(),t.end(),0.0)/t.size(),*std::max_element(t.begin(),t.end()));std::fflush(stdout);
 }
}
