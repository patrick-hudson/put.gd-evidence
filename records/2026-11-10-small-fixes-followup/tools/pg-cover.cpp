#include <QApplication>
#include <QPainter>
#include <QWidget>
class Cover:public QWidget{public:Cover():QWidget(nullptr,Qt::FramelessWindowHint|Qt::WindowStaysOnTopHint|Qt::X11BypassWindowManagerHint){setGeometry(0,0,1920,1080);show();}void paintEvent(QPaintEvent*)override{QPainter p(this);p.fillRect(rect(),QColor(80,140,180));p.setPen(Qt::white);QFont f;f.setPixelSize(30);p.setFont(f);p.drawText(100,100,"put.gd #1380 - synthetic Cinnamon/X11 capture check");}};
int main(int argc,char**argv){QApplication app(argc,argv);Cover cover;return app.exec();}
