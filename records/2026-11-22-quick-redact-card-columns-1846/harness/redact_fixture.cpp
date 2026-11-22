// #1839/#1840/#1846/#1850 desktop fixture, not part of the product or a PR. Draws a
// 1920x1080 page of synthetic test text with Qt (as the corpus harness does), writes
// fixture.png, labels.png (16-bit word number where that word's coverage >= 32) and
// words.json in #1842's checker format, then recognizes the page with the real
// putgd-ocr and prints what find() matches, so the page is known to show each case.
//   redact_fixture --helper PATH --data DIR --out DIR
#include "core/TextJob.h"
#include "editor/QuickRedact.h"
#include "editor/TextLayer.h"
#include <QDir>
#include <QFile>
#include <QGuiApplication>
#include <QImage>
#include <QJsonArray>
#include <QJsonDocument>
#include <QJsonObject>
#include <QPainter>
#include <QTextLayout>
#include <QGlyphRun>
#include <cstdio>
using namespace putgd;
namespace qr=editor::quickRedact;
struct Line {QString text;QList<int> matched;};
struct Block {QString name,family;int px;int x,y;QColor paper,ink;QList<Line> lines;};
int main(int argc,char** argv){
 qputenv("QT_QPA_PLATFORM","offscreen");
 QGuiApplication app(argc,argv);
 QString helper,out;QStringList data;
 const auto args=app.arguments();
 for(int i=1;i<args.size();++i){if(args[i]=="--helper")helper=args[++i];else if(args[i]=="--data")data.append(args[++i]);else if(args[i]=="--out")out=args[++i];}
 const QString token=QString("gh")+"p_"+"aB3dE5fG7hJ9kL1mN3pQ"+"5rS7tU9vW1xY3zA5";
 const QString hex=QString("\"6311d6de7be2f57b64c74d411a0b3")+"7935201bc28fc32d62a927d6cfb5d343";
 const QList<Line> email{{"Please write to jane.doe@example.com before Friday",{3}},{"Contact us. bob@example.com today",{2}},{"Reach me at jane.doe@example.com",{3}}};
 const QList<Block> blocks{
  {"email-rhd-10","Red Hat Display",10,40,30,Qt::white,Qt::black,email},
  {"email-rhd-9","Red Hat Display",9,40,110,Qt::white,Qt::black,email},
  {"email-rhd-10-dark","Red Hat Display",10,40,190,QColor(30,30,30),QColor(230,230,230),email},
  {"token-serif-14","Liberation Serif",14,40,560,Qt::white,Qt::black,{{"Your token "+token+" was leaked today",{2}},{"Bearer "+token+" (expires next week).",{1}}}},
  {"token-sans-18","Noto Sans",18,40,650,Qt::white,QColor(20,20,20),{{"Your token "+token+" was leaked today",{2}}}},
  {"cards-sans-16","Noto Sans",16,40,280,Qt::white,QColor(20,20,20),{{"Card 4539 1488 0343 6467 Card 5425 2334 3010 9903",{1,2,3,4,6,7,8,9}},{"Card 4111 1111 1111 1111 Card 5555 5555 5555 4444",{1,2,3,4,6,7,8,9}}}},
  {"columns-left","Noto Sans",16,40,1000,Qt::white,QColor(20,20,20),{{"Card 4111 1111 1111 1111",{1,2,3,4}}}},
  {"columns-right","Noto Sans",16,1200,1000,Qt::white,QColor(20,20,20),{{"MC 5555 5555 5555 4444",{1,2,3,4}}}},
  {"hex-mono-15","Noto Sans Mono",15,40,380,Qt::white,QColor(30,30,30),{{"SIGNING_HEX =",{}},{hex,{0}},{"edc\"",{0}},{"OWNER = \"ops-alerts\"",{}}}},
 };
 QImage page(1920,1080,QImage::Format_RGB32);page.fill(Qt::white);
 QImage labels(page.size(),QImage::Format_Grayscale16);labels.fill(0);
 QJsonArray words;int number=0;
 for(const auto& block:blocks){
  QFont font(block.family);font.setPixelSize(block.px);font.setHintingPreference(QFont::PreferDefaultHinting);
  const int lineHeight=int(block.px*1.9);
  {QPainter p(&page);p.fillRect(QRect(block.x-20,block.y-14,block.x>=1000?700:1100,lineHeight*int(block.lines.size())+10),block.paper);}
  for(int l=0;l<block.lines.size();++l){
   const auto& line=block.lines[l];
   QTextLayout layout(line.text,font);layout.beginLayout();auto tl=layout.createLine();tl.setLineWidth(1e6);tl.setPosition({0,0});layout.endLayout();
   const QPointF origin(block.x,block.y+l*lineHeight);
   {QPainter p(&page);p.setPen(block.ink);p.setRenderHint(QPainter::TextAntialiasing);for(const auto& run:layout.glyphRuns())p.drawGlyphRun(origin,run);}
   const auto parts=line.text.split(' ');int from=0;
   for(int w=0;w<parts.size();++w){
    QImage mask(page.size(),QImage::Format_Grayscale8);mask.fill(0);
    {QPainter q(&mask);q.setPen(Qt::white);q.setRenderHint(QPainter::TextAntialiasing);for(const auto& run:layout.glyphRuns(from,int(parts[w].size())))q.drawGlyphRun(origin,run);}
    from+=int(parts[w].size())+1;++number;
    QRect box;
    for(int y=0;y<mask.height();++y){const auto* s=mask.constScanLine(y);auto* t=reinterpret_cast<quint16*>(labels.scanLine(y));for(int x=0;x<mask.width();++x)if(s[x]>=32){t[x]=quint16(number);box=box.united(QRect(x,y,1,1));}}
    words.append(QJsonObject{{"n",number},{"block",block.name},{"line",l},{"text",parts[w]},{"box",QJsonArray{box.left(),box.top(),box.right()+1,box.bottom()+1}},{"role",line.matched.contains(w)?"matched":"neighbour"}});
   }
  }
 }
 QDir().mkpath(out);
 page.save(QDir(out).filePath("fixture.png"));labels.save(QDir(out).filePath("labels.png"));
 QFile f(QDir(out).filePath("words.json"));f.open(QIODevice::WriteOnly);f.write(QJsonDocument(words).toJson());f.close();
 putgd::TextJob job(helper);if(!data.isEmpty())job.setDataDirectories(data);
 TextJob::Options options;options.languages={"eng"};options.candidates=true;
 Error error;const auto result=job.recognize(page,options,error);
 if(error){std::fprintf(stderr,"%s\n",qPrintable(error.code));return 1;}
 QList<editor::RecognizedWord> candidates;for(const auto& c:result.candidates)candidates.append({c.text,c.rect,c.confidence,0});
 if(qEnvironmentVariableIsSet("DUMP"))for(const auto& c:candidates)std::printf("W %s %d %d %d %d\n",qPrintable(c.text),c.rect.x(),c.rect.y(),c.rect.width(),c.rect.height());
 QList<editor::RecognizedCode> codes;editor::TextLayer::exclude(candidates,codes,{});
 for(const auto& match:qr::find(candidates,{"card","key","email"})){QStringList t;for(const int w:match.words)t.append(candidates.at(w).text);std::printf("%s: %s\n",qPrintable(match.category),qPrintable(t.join(' ')));}
 return 0;
}
