#include <QApplication>
#include <QColorDialog>
#include <QMessageBox>
#include <QWidget>
#include <QTimer>
#include <QLabel>
#include <QVBoxLayout>
#include <cstdio>
// usage: dlgtest PARENT(frameless|decorated) DIALOG(getcolor|nonmodal|windowmodal|msgbox)
int main(int argc,char** argv){
  QApplication app(argc,argv);
  const QString parentMode=argc>1?argv[1]:"frameless", mode=argc>2?argv[2]:"getcolor";
  QWidget w; w.setWindowTitle("dlgtest parent");
  if(parentMode=="frameless")w.setWindowFlag(Qt::FramelessWindowHint,true);
  auto* l=new QVBoxLayout(&w); auto* lab=new QLabel(parentMode+" / "+mode,&w); QFont f=lab->font(); f.setPointSize(28); lab->setFont(f); l->addWidget(lab);
  w.setStyleSheet("background:#335;color:white"); w.resize(1000,700); w.show();
  QTimer::singleShot(800,&w,[&]{
    if(mode=="getcolor"){ auto c=QColorDialog::getColor(Qt::blue,&w,"Custom color"); printf("color %s\n",qPrintable(c.name())); }
    else { auto* d=new QColorDialog(Qt::blue,&w); d->setWindowTitle("Custom color");
      if(mode=="windowmodal")d->setWindowModality(Qt::WindowModal);
      if(mode=="appmodal")d->setWindowModality(Qt::ApplicationModal);
      d->show(); }
  });
  return app.exec();
}
