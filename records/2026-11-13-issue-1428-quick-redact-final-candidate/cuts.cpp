// Throwaway: the engine's own profile and strip cuts for one page (#1428).
#include "ocr/Layout.h"
#include <QCoreApplication>
#include <QImage>
#include <cstdio>
using namespace putgd::ocr;
int main(int argc,char** argv){
 QCoreApplication app(argc,argv);
 auto image=QImage(argv[1]).convertToFormat(QImage::Format_Grayscale8);
 GreyView view{image.constBits(),image.width(),image.height(),int(image.bytesPerLine())};
 const auto profile=measure(view,{});
 printf("size %dx%d lineHeight %d dark %d blank threshold %d\n",image.width(),image.height(),profile.lineHeight,profile.dark,std::max(2,image.width()/256));
 for(int y=atoi(argv[2]);y<=atoi(argv[3]);++y)printf("row %d ink %d%s\n",y,profile.rowInk.at(y),profile.blank(y,image.width())?" blank":"");
 for(int parts:{2,4,6,8}){printf("parts %d:",parts);for(const auto& b:strips(profile,image.width(),image.height(),parts))printf(" [%d,%d)",b.top,b.bottom);printf("\n");}
}
