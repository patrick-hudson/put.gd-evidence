#include "editor/EditorCanvas.h"
#include "editor/EditorCommands.h"
#include <QApplication>
#include <QElapsedTimer>
#include <QJsonArray>
#include <cstdio>
#include <numeric>
#include <algorithm>
using namespace putgd::editor;
class Canvas:public EditorCanvas {
public:using EditorCanvas::EditorCanvas;std::vector<double> times;
protected:void paintEvent(QPaintEvent* event)override{QElapsedTimer clock;clock.start();EditorCanvas::paintEvent(event);times.push_back(clock.nsecsElapsed()/1e6);}
};
int main(int argc,char**argv){QApplication app(argc,argv);std::printf("build,width,height,mask,samples,mean_ms,worst_ms\n");
 for(QSize size:{QSize(3840,2160),QSize(6000,4000)})for(int mask=0;mask<3;++mask){
 QImage source(size,QImage::Format_RGB32);source.fill(QColor(240,80,210));EditDocument doc(source);
 if(mask){const QRect box=mask==1?QRect(100,100,600,50):QRect(100,100,size.width()-200,size.height()-200);QJsonArray ids;QString code,message;if(!Commands::apply(doc,{QJsonObject{{"op","add"},{"shape",QJsonObject{{"kind","redact"},{"rect",QJsonArray{box.x(),box.y(),box.width(),box.height()}}}}}},ids,code,message))return 2;}
 Canvas canvas(doc);canvas.resize(1200,800);canvas.fit();QImage output(canvas.size(),QImage::Format_RGB32);
 for(int i=0;i<20;++i)canvas.render(&output);canvas.times.clear();
 for(int i=0;i<300;++i)canvas.render(&output);
 const auto& t=canvas.times;std::printf("%s,%d,%d,%s,%zu,%.4f,%.4f\n",argv[1],size.width(),size.height(),mask==0?"none":mask==1?"small":"large",t.size(),std::accumulate(t.begin(),t.end(),0.0)/t.size(),*std::max_element(t.begin(),t.end()));std::fflush(stdout);
 }
}
