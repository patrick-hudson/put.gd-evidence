// #1849/#1854 local tool, never committed: recognizes a page PNG with the real
// putgd-ocr, finds card/key/email matches, and writes the page with every mark
// filled black (what Quick redact would show).
//   redact_page --helper PATH --data DIR --page IN.png --covered OUT.png
#include "core/TextJob.h"
#include "editor/QuickRedact.h"
#include "editor/TextLayer.h"
#include <QGuiApplication>
#include <QImage>
#include <QPainter>
#include <cstdio>
using namespace putgd;
namespace qr=editor::quickRedact;
int main(int argc,char** argv){
 qputenv("QT_QPA_PLATFORM","offscreen");
 QGuiApplication app(argc,argv);
 QString helper,in,outPath;QStringList data;
 const auto args=app.arguments();
 for(int i=1;i<args.size();++i){if(args[i]=="--helper")helper=args[++i];else if(args[i]=="--data")data.append(args[++i]);else if(args[i]=="--page")in=args[++i];else if(args[i]=="--covered")outPath=args[++i];}
 QImage page(in);page=page.convertToFormat(QImage::Format_RGB32);
 putgd::TextJob job(helper);if(!data.isEmpty())job.setDataDirectories(data);
 TextJob::Options options;options.languages={"eng"};options.candidates=true;
 Error error;const auto result=job.recognize(page,options,error);
 if(error){std::fprintf(stderr,"%s\n",qPrintable(error.code));return 1;}
 QList<editor::RecognizedWord> candidates;for(const auto& c:result.candidates)candidates.append({c.text,c.rect,c.confidence,0});
 if(qEnvironmentVariableIsSet("WORDS"))for(const auto& c:candidates)std::printf("W %s %d %d %d %d\n",qPrintable(c.text),c.rect.x(),c.rect.y(),c.rect.width(),c.rect.height());
 QList<editor::RecognizedCode> codes;editor::TextLayer::exclude(candidates,codes,{});
 QImage covered=page;QPainter p(&covered);
 for(const auto& match:qr::find(candidates,{"card","key","email"})){
  QStringList t;for(const int w:match.words)t.append(candidates.at(w).text);
  QStringList r;for(const auto& m:qr::marks(candidates,match,page.rect(),page)){p.fillRect(m,Qt::black);r.append(QString("%1,%2-%3,%4").arg(m.left()).arg(m.top()).arg(m.right()).arg(m.bottom()));}
  std::printf("%s: %s -> %s\n",qPrintable(match.category),qPrintable(t.join(' ')),qPrintable(r.join(' ')));
 }
 p.end();if(!outPath.isEmpty())covered.save(outPath);
 return 0;
}
