#include "editor/EditorCommands.h"
#include <QApplication>
#include <QJsonArray>
using namespace putgd::editor;
int main(int argc,char**argv){QApplication app(argc,argv);EditDocument doc(QImage(QString::fromLocal8Bit(argv[1])));QJsonArray ids;QString code,message;QJsonArray ops;
 if(QString::fromLocal8Bit(argv[3])=="edge")ops.append(QJsonObject{{"op","add"},{"shape",QJsonObject{{"kind","arrow"},{"from",QJsonArray{245,455}},{"to",QJsonArray{325,455}},{"color","#D7263D"},{"width",4}}}});
 else ops.append(QJsonObject{{"op","add"},{"shape",QJsonObject{{"kind","text"},{"at",QJsonArray{20,20}},{"text",QString::fromLocal8Bit(argv[3])},{"fontPixels",20},{"color","#D7263D"}}}});
 if(!Commands::apply(doc,ops,ids,code,message))return 1;return doc.render().save(QString::fromLocal8Bit(argv[2]))?0:2;}
