#include <QApplication>
#include <QTextEdit>
#include <QFile>
#include <QTimer>
#include <QVBoxLayout>
#include <QLabel>
int main(int argc,char**argv){QApplication app(argc,argv);QWidget window;QVBoxLayout layout(&window);QLabel label(QString::fromLocal8Bit(argv[3]));label.setStyleSheet("color:#ffb84d;font-size:22px;font-weight:bold");layout.addWidget(&label);QFile f(QString::fromLocal8Bit(argv[1]));f.open(QIODevice::ReadOnly);QTextEdit terminal;terminal.setReadOnly(true);terminal.setPlainText(QString::fromUtf8(f.readAll()));terminal.setStyleSheet("background:#151515;color:#eeeeee;font:18px monospace");layout.addWidget(&terminal);window.resize(1100,600);window.show();QTimer::singleShot(1200,&app,[&]{window.grab().save(QString::fromLocal8Bit(argv[2]));app.quit();});return app.exec();}
