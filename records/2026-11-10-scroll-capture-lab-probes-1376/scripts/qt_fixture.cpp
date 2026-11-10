#include <QApplication>
#include <QPlainTextEdit>
#include <QScrollBar>
#include <cstdio>
int main(int argc,char**argv){QApplication a(argc,argv);QPlainTextEdit w;QString s;for(int i=0;i<1500;i++)s+=QString("Row %1 — standalone Qt scroll probe\n").arg(i,4,10,QChar('0'));w.setPlainText(s);w.setReadOnly(true);w.setWindowTitle("Scroll probe Qt text");QObject::connect(w.verticalScrollBar(),&QScrollBar::valueChanged,[](int v){printf("qt_scrollbar=%d\n",v);fflush(stdout);});w.showMaximized();return a.exec();}
