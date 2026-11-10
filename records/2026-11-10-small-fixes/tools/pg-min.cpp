#include <QApplication>
#include <QTimer>
#include <QWindow>
#include <cstdio>
int main(int argc,char**argv){QGuiApplication::setDesktopSettingsAware(false);fprintf(stderr,"BEFORE APP\n");QApplication app(argc,argv);fprintf(stderr,"AFTER APP\n");{QWindow cursor;cursor.create();cursor.setCursor(Qt::CrossCursor);fprintf(stderr,"CURSOR CREATED\n");}fprintf(stderr,"CURSOR DESTROYED\n");QTimer::singleShot(100,&app,&QCoreApplication::quit);return QCoreApplication::exec();}
