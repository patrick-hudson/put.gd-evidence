// Throwaway diagnosis tool for #1428 Quick redact (never committed).
//   qr_dump recognize HELPER OUT.json PAGE.png...   real putgd-ocr, words + unfiltered candidates
//   qr_dump match IN.json OUT.json                   quickRedact::find + marks on saved candidates
#include "core/TextJob.h"
#include "editor/QuickRedact.h"
#include "editor/TextLayer.h"
#include <QCoreApplication>
#include <QElapsedTimer>
#include <QFile>
#include <QFileInfo>
#include <QImageReader>
#include <QJsonArray>
#include <QJsonDocument>
#include <QJsonObject>
using namespace putgd;
static QJsonArray rect(const QRect& r){return {r.x(),r.y(),r.width(),r.height()};}
static QJsonArray words(const QList<editor::RecognizedWord>& list){QJsonArray a;for(const auto& w:list)a.append(QJsonObject{{"text",w.text},{"rect",rect(w.rect)},{"confidence",w.confidence},{"line",w.line}});return a;}
static QList<editor::RecognizedWord> parse(const QJsonArray& a){QList<editor::RecognizedWord> out;for(const auto& v:a){const auto o=v.toObject();const auto r=o["rect"].toArray();out.append({o["text"].toString(),QRect(r[0].toInt(),r[1].toInt(),r[2].toInt(),r[3].toInt()),o["confidence"].toInt(),o["line"].toInt()});}return out;}
static QJsonArray match(const QList<editor::RecognizedWord>& c,const QSize& size){
 QJsonArray out;
 for(const auto& m:editor::quickRedact::find(c,editor::quickRedact::categories())){QJsonArray ws,ms;for(int w:m.words)ws.append(w);for(const auto& r:editor::quickRedact::marks(c,m,QRect(QPoint(0,0),size)))ms.append(rect(r));out.append(QJsonObject{{"category",m.category},{"words",ws},{"marks",ms}});}
 return out;
}
int main(int argc,char** argv){
 QCoreApplication app(argc,argv);const auto args=app.arguments();
 if(args.size()>=5&&args[1]=="recognize"){
  QJsonObject pages;
  for(int i=4;i<args.size();++i){
   QImageReader reader(args[i],"png");reader.setAutoDetectImageFormat(false);const auto image=reader.read();
   textjob::Options options;options.words=true;options.candidates=true;options.languages={"eng"};
   Error error;QElapsedTimer t;t.start();const auto result=TextJob(args[2]).recognize(TextJob::grey(image),options,error);
   QList<editor::RecognizedWord> cand,wd;QList<editor::RecognizedCode> none;
   for(const auto& w:result.candidates)cand.append({w.text,w.rect,w.confidence,0});
   for(const auto& w:result.words)wd.append({w.text,w.rect,w.confidence,0});
   editor::TextLayer::exclude(cand,none,{});editor::TextLayer::exclude(wd,none,{});
   pages[QFileInfo(args[i]).fileName()]=QJsonObject{{"error",error.code},{"ms",double(t.elapsed())},{"width",image.width()},{"height",image.height()},{"truncated",result.truncated},{"candidates",words(cand)},{"words",words(wd)},{"matches",match(cand,image.size())}};
   fprintf(stderr,"%s %s %lld ms %d candidates\n",qPrintable(args[i]),qPrintable(error.code),qint64(t.elapsed()),int(cand.size()));
  }
  QFile f(args[3]);f.open(QIODevice::WriteOnly);f.write(QJsonDocument(pages).toJson(QJsonDocument::Compact));return 0;
 }
 if(args.size()==4&&args[1]=="match"){
  QFile in(args[2]);in.open(QIODevice::ReadOnly);auto pages=QJsonDocument::fromJson(in.readAll()).object();
  for(auto it=pages.begin();it!=pages.end();++it){auto p=it.value().toObject();auto c=parse(p["candidates"].toArray());QList<editor::RecognizedCode> none;editor::TextLayer::exclude(c,none,{});p["candidates"]=words(c);p["matches"]=match(c,QSize(p["width"].toInt(),p["height"].toInt()));it.value()=p;}
  QFile f(args[3]);f.open(QIODevice::WriteOnly);f.write(QJsonDocument(pages).toJson(QJsonDocument::Compact));return 0;
 }
 fprintf(stderr,"usage\n");return 2;
}
