#include "ui/EditorWindow.h"
#include "editor/EditorCommands.h"
#include <QApplication>
#include <QTimer>
#include <QPainter>
#include <QJsonArray>
#include <QFile>
#include <QTextEdit>
using namespace putgd;using namespace putgd::editor;
int main(int argc,char**argv){
 QApplication app(argc,argv);QImage image(1200,760,QImage::Format_RGB32);image.fill(Qt::white);const QRect mask(401,279,357,213);
 {QPainter p(&image);p.fillRect(mask,Qt::magenta);p.setPen(Qt::black);QFont f;p.setFont(f);p.drawText(80,100,"Synthetic covered content: inspect the right and bottom edges at Fit zoom");}
 EditDocument doc(image);QJsonArray created;QString code,message;Commands::apply(doc,{QJsonObject{{"op","add"},{"shape",QJsonObject{{"kind","redact"},{"rect",QJsonArray{mask.x(),mask.y(),mask.width(),mask.height()}}}}}},created,code,message);
 EditorWindow window(doc);window.resize(1200,850);window.show();
 QTimer::singleShot(1200,&app,[&]{
 auto shot=window.grab().toImage();
 auto& canvas=window.canvas();const auto origin=canvas.mapTo(&window,QPoint{});const auto z=canvas.zoom();const QPoint edge=origin+QPoint(qRound((canvas.width()-image.width()*z)/2+(mask.x()+mask.width())*z),qRound((canvas.height()-image.height()*z)/2+(mask.y()+mask.height())*z));EditDocument annotated(shot);QJsonArray ids;
 Commands::apply(annotated,{QJsonObject{{"op","add"},{"shape",QJsonObject{{"kind","text"},{"at",QJsonArray{30,90}},{"text",QString::fromLocal8Bit(argv[2])},{"fontPixels",22},{"color","#D7263D"}}}}},ids,code,message);
 Commands::apply(annotated,{QJsonObject{{"op","add"},{"shape",QJsonObject{{"kind","arrow"},{"from",QJsonArray{edge.x()+80,edge.y()+60}},{"to",QJsonArray{edge.x(),edge.y()}},{"color","#D7263D"},{"width",4}}}}},ids,code,message);
 annotated.render().save(QString::fromLocal8Bit(argv[1]));app.quit();});return app.exec();
}
