// #1838 measurement harness, not part of the product or a PR. Renders lines of
// test text in many fonts and sizes, recognizes them with the real putgd-ocr,
// finds matches with quickRedact::find, and measures, for the shipped
// markBoxes and the pre-#1838 copy below:
//  - leaked: ink pixels of matched words left outside every cover (must be 0);
//  - neighbour: ink pixels of unmatched words inside a cover.
// Ground truth ink comes from drawing each word alone at its laid-out place.
//   redact_cover --helper PATH [--data DIR] [--out DIR] [--fonts a,b] [--sizes 11,13]
#include "core/TextJob.h"
#include "editor/QuickRedact.h"
#include "editor/TextLayer.h"
#include <QDir>
#include <QDirIterator>
#include <QFontDatabase>
#include <QFontMetricsF>
#include <QGuiApplication>
#include <QImage>
#include <QJsonArray>
#include <QJsonDocument>
#include <QJsonObject>
#include <QPainter>
#include <QLinearGradient>
#include <QTextLayout>
#include <QGlyphRun>
#include <cmath>
#include <cstdio>

using namespace putgd;
using editor::RecognizedWord;
namespace qr=editor::quickRedact;

namespace {
// markBoxes as it was before #1838 (nightly 4608d913a).
QList<QRect> oldMarks(const QList<RecognizedWord>& candidates,const qr::Match& match,const QRect& bounds){
 QList<int> words;for(const int index:match.words)if(index>=0&&index<candidates.size())words.append(index);
 std::stable_sort(words.begin(),words.end(),[&](int a,int b){return candidates.at(a).rect.center().y()<candidates.at(b).rect.center().y();});
 QList<int> heights;for(const int w:words)heights.append(candidates.at(w).rect.height());std::sort(heights.begin(),heights.end());
 const double tolerance=qMax(2.0,heights.isEmpty()?2.0:heights.at(heights.size()/2)*0.5);
 struct Row {QRect box;int characters=0;double centre=0;int count=0;};
 QList<Row> rows;
 for(const int w:words){
  const auto& word=candidates.at(w);const double y=word.rect.center().y();
  if(rows.isEmpty()||std::abs(y-rows.last().centre)>tolerance)rows.append(Row{});
  auto& row=rows.last();row.box=row.box.united(word.rect);row.characters+=int(word.text.size());++row.count;row.centre+=(y-row.centre)/row.count;
 }
 QList<QRect> out;
 for(const auto& row:std::as_const(rows)){
  const auto& box=row.box;const int pad=qMax(1,(box.height()+3)/4);const int side=qMax(pad,box.width()*3/qMax(2,2*row.characters));
  const auto mark=box.adjusted(-side,-pad,side,pad).intersected(bounds);if(!mark.isEmpty())out.append(mark);
 }
 return out;
}
// The #1838 rule with a floor: whatever a neighbour leaves, at least `floor`
// of the edge word's glyph either side.
QList<QRect> variantMarks(const QList<RecognizedWord>& candidates,const qr::Match& match,const QRect& bounds,double floor){
 QList<int> words;for(const int index:match.words)if(index>=0&&index<candidates.size())words.append(index);
 std::stable_sort(words.begin(),words.end(),[&](int a,int b){return candidates.at(a).rect.center().y()<candidates.at(b).rect.center().y();});
 QList<int> heights;for(const int w:words)heights.append(candidates.at(w).rect.height());std::sort(heights.begin(),heights.end());
 const double tolerance=qMax(2.0,heights.isEmpty()?2.0:heights.at(heights.size()/2)*0.5);
 struct Row {QRect box;double centre=0;int count=0;int first=-1;int last=-1;};
 QList<Row> rows;
 for(const int w:words){
  const auto& word=candidates.at(w);const double y=word.rect.center().y();
  if(rows.isEmpty()||std::abs(y-rows.last().centre)>tolerance)rows.append(Row{});
  auto& row=rows.last();row.box=row.box.united(word.rect);++row.count;row.centre+=(y-row.centre)/row.count;
  if(row.first<0||word.rect.left()<candidates.at(row.first).rect.left())row.first=w;
  if(row.last<0||word.rect.right()>candidates.at(row.last).rect.right())row.last=w;
 }
 const auto glyph=[&](int w){const auto& word=candidates.at(w);const auto n=std::count_if(word.text.cbegin(),word.text.cend(),[](QChar c){return !c.isLowSurrogate()&&!c.isSpace();});return double(word.rect.width())/double(qMax<qsizetype>(1,n));};
 QList<QRect> out;
 for(const auto& row:std::as_const(rows)){
  const auto& box=row.box;const int pad=qMax(1,(box.height()+3)/4);
  int left=box.left()-qMax(pad,int(std::ceil(glyph(row.first)*1.5)));
  int right=box.right()+qMax(pad,int(std::ceil(glyph(row.last)*1.5)));
  for(qsizetype i=0;i<candidates.size();++i){
   if(match.words.contains(int(i)))continue;
   const auto& other=candidates.at(i).rect;
   if(other.isEmpty()||std::abs(other.center().y()-row.centre)>tolerance)continue;
   const int gap=qMax(1,other.height()/10);
   if(other.right()<box.left())left=qMax(left,qMin(box.left(),other.right()+1+gap));
   else if(other.left()>box.right())right=qMin(right,qMax(box.right(),other.left()-1-gap));
  }
  left=qMin(left,box.left()-int(std::ceil(glyph(row.first)*floor)));
  right=qMax(right,box.right()+int(std::ceil(glyph(row.last)*floor)));
  const auto mark=QRect(QPoint(left,box.top()-pad),QPoint(right,box.bottom()+pad)).intersected(bounds);if(!mark.isEmpty())out.append(mark);
 }
 return out;
}
struct Line {QString text;QList<int> matched;QString category;};
struct Word {QString text;int line=0;bool matched=false;QImage ink;QRect inkBox;};
}

int main(int argc,char** argv){
 qputenv("QT_QPA_PLATFORM","offscreen");
 QGuiApplication app(argc,argv);
 if(const auto dir=qEnvironmentVariable("FIXTURE_FONTS");!dir.isEmpty()){QDirIterator it(dir,{"*.otf","*.ttf"});while(it.hasNext())QFontDatabase::addApplicationFont(it.next());}
 QString helper,out;QStringList data,fonts;QList<int> sizes{10,11,13,16,20,24,32};
 const auto args=app.arguments();
 for(int i=1;i<args.size();++i){
  const auto& a=args[i];
  if(a=="--helper"&&i+1<args.size())helper=args[++i];
  else if(a=="--data"&&i+1<args.size())data.append(args[++i]);
  else if(a=="--out"&&i+1<args.size())out=args[++i];
  else if(a=="--fonts"&&i+1<args.size())fonts=args[++i].split(',');
  else if(a=="--sizes"&&i+1<args.size()){sizes.clear();for(const auto& s:args[++i].split(','))sizes.append(s.toInt());}
 }
 if(fonts.isEmpty())fonts=QFontDatabase::families();
 const QString token=QString("gh")+"p_"+"aB3dE5fG7hJ9kL1mN3pQ"+"5rS7tU9vW1xY3zA5";
 const QList<Line> lines{
  {"Card 4111 1111 1111 1111",{1,2,3,4},"card"},
  {"Your token "+token+" was leaked today",{2},"key"},
  {"Please write to jane.doe@example.com before Friday",{3},"email"},
  {"4111 1111 1111 1111 is on file",{0,1,2,3},"card"},
  {"Reach me at jane.doe@example.com",{3},"email"},
 };
 putgd::TextJob job(helper);if(!data.isEmpty())job.setDataDirectories(data);
 TextJob::Options options;options.languages={"eng"};options.candidates=true;
 QJsonArray rows;
 struct Total {qint64 leaked=0,neighbour=0,neighbourWords=0,cases=0,leakCases=0,neighbourCases=0;};
 const QStringList versions{"old","shipped"};QList<Total> totals(versions.size());
 qint64 missed=0,expected=0;
 for(const auto& family:fonts){
  for(const int px:sizes){
   for(const QString theme:{QString("light"),QString("dark"),QString("tint"),QString("noise"),QString("gradient")}){
    const bool dark=theme=="dark"||theme=="tint";
    QFont font(family);font.setPixelSize(px);font.setHintingPreference(QFont::PreferDefaultHinting);
    const QFontMetricsF metrics(font);
    const int lineHeight=int(std::ceil(metrics.height()*1.6));
    const int margin=qMax(6,px/2);
    int width=0;for(const auto& line:lines)width=qMax(width,int(std::ceil(metrics.horizontalAdvance(line.text))));
    const QSize size(width+2*margin+px,lineHeight*int(lines.size())+2*margin);
    const QColor paper=theme=="dark"?QColor(30,30,30):theme=="tint"?QColor(42,93,176):theme=="noise"?QColor(236,236,236):Qt::white;
    const QColor ink=theme=="dark"?QColor(230,230,230):theme=="tint"?QColor(255,255,255):theme=="noise"?QColor(40,40,40):Qt::black;
    QImage image(size,QImage::Format_RGB32);image.fill(paper);
    if(theme=="noise"){quint32 seed=px*7919u+uint(qHash(family));for(int y=0;y<size.height();++y){auto* row=reinterpret_cast<QRgb*>(image.scanLine(y));for(int x=0;x<size.width();++x){seed=seed*1664525u+1013904223u;const int d=int((seed>>24)%13)-6;row[x]=qRgb(236+d,236+d,236+d);}}}
    if(theme=="gradient"){QPainter g(&image);QLinearGradient lg(0,0,size.width(),0);lg.setColorAt(0,QColor(255,255,255));lg.setColorAt(1,QColor(200,215,235));g.fillRect(image.rect(),lg);}
    QList<Word> words;
    {
     QPainter p(&image);p.setPen(ink);p.setRenderHint(QPainter::TextAntialiasing);
     for(int l=0;l<lines.size();++l){
      // One layout per line: the picture and every word's mask are drawn from
      // the same glyph runs, so the masks sit exactly on the picture's ink.
      QTextLayout layout(lines[l].text,font);layout.beginLayout();auto tl=layout.createLine();tl.setLineWidth(1e6);tl.setPosition({0,0});layout.endLayout();
      const QPointF origin(margin,margin+l*lineHeight);
      for(const auto& run:layout.glyphRuns())p.drawGlyphRun(origin,run);
      const auto parts=lines[l].text.split(' ');
      int from=0;
      for(int w=0;w<parts.size();++w){
       Word word{parts[w],l,lines[l].matched.contains(w),QImage(size,QImage::Format_Grayscale8),{}};
       word.ink.fill(0);
       QPainter q(&word.ink);q.setPen(Qt::white);q.setRenderHint(QPainter::TextAntialiasing);
       for(const auto& run:layout.glyphRuns(from,int(parts[w].size())))q.drawGlyphRun(origin,run);
       q.end();from+=int(parts[w].size())+1;
       for(int y=0;y<size.height();++y){const auto* s=word.ink.constScanLine(y);for(int xx=0;xx<size.width();++xx)if(s[xx]>=32)word.inkBox=word.inkBox.united(QRect(xx,y,1,1));}
       words.append(word);
      }
     }
    }
    // Ground truth check: picture ink (32 from the paper) that no word's mask holds.
    qint64 stray=0;
    for(int y=0;y<size.height();++y){const auto* row=reinterpret_cast<const QRgb*>(image.constScanLine(y));
     for(int x=0;x<size.width();++x){if(std::abs(qGray(row[x])-qGray(paper.rgb()))<32)continue;bool held=false;for(const auto& w:words)if(w.ink.constScanLine(y)[x]>0){held=true;break;}if(!held)++stray;}}
    if(theme=="gradient"||theme=="noise")stray=0;
    if(stray)std::fprintf(stderr,"%s %d %s: %lld ink pixels in no mask\n",qPrintable(family),px,qPrintable(theme),stray);
    Error error;const auto result=job.recognize(image,options,error);
    if(error){std::fprintf(stderr,"%s %d: %s\n",qPrintable(family),px,qPrintable(error.code));continue;}
    QList<RecognizedWord> candidates;for(const auto& c:result.candidates)candidates.append({c.text,c.rect,c.confidence,0});
    QList<editor::RecognizedCode> codes;editor::TextLayer::exclude(candidates,codes,{});
    const auto found=qr::find(candidates,{"card","key","email"});
    const QRect bounds(QPoint(0,0),size);
    QJsonArray matchDump;
    for(const auto& match:found){QStringList t;QJsonArray boxes;for(const int w:match.words){t.append(candidates.at(w).text);const auto r=candidates.at(w).rect;boxes.append(QJsonArray{r.x(),r.y(),r.width(),r.height()});}
     QJsonArray nm,om;for(const auto& r:qr::marks(candidates,match,bounds,image))nm.append(QJsonArray{r.x(),r.y(),r.width(),r.height()});for(const auto& r:oldMarks(candidates,match,bounds))om.append(QJsonArray{r.x(),r.y(),r.width(),r.height()});
     matchDump.append(QJsonObject{{"category",match.category},{"text",t.join(' ')},{"boxes",boxes},{"new",nm},{"old",om}});}
    QJsonArray candDump;for(const auto& c:candidates)candDump.append(QJsonObject{{"t",c.text},{"r",QJsonArray{c.rect.x(),c.rect.y(),c.rect.width(),c.rect.height()}}});
    QJsonArray truth;for(const auto& w:words)truth.append(QJsonObject{{"t",w.text},{"line",w.line},{"m",w.matched},{"ink",QJsonArray{w.inkBox.x(),w.inkBox.y(),w.inkBox.width(),w.inkBox.height()}}});
    rows.append(QJsonObject{{"font",family},{"px",px},{"theme",theme},{"code","detail"},{"matches",matchDump},{"candidates",candDump},{"truth",truth}});
    for(int version=0;version<versions.size();++version){
     QList<QRect> covers;
     for(const auto& match:found){
      if(version==0)covers+=oldMarks(candidates,match,bounds);
      else if(version==1)covers+=qr::marks(candidates,match,bounds,image);
      else if(version==2)covers+=qr::marks(candidates,match,bounds);
      else covers+=variantMarks(candidates,match,bounds,QStringView(versions[version]).mid(1).toInt()/100.0);
     }
     QImage covered(size,QImage::Format_Grayscale8);covered.fill(0);
     {QPainter c(&covered);for(const auto& r:covers)c.fillRect(r,Qt::white);}
     QJsonArray perLine;
     for(int l=0;l<lines.size();++l){
      qint64 leaked=0,neighbour=0,neighbourWords=0;bool any=false;QJsonArray who;
      for(const auto& word:words){
       if(word.line!=l)continue;
       qint64 in=0,outside=0;
       for(int y=word.inkBox.top();y<=word.inkBox.bottom();++y){
        const auto* s=word.ink.constScanLine(y);const auto* c=covered.constScanLine(y);
        for(int x=word.inkBox.left();x<=word.inkBox.right();++x){if(s[x]<32)continue;if(c[x])++in;else ++outside;}
       }
       bool taken=false;
       if(!word.matched)for(const auto& match:found)for(const int w:match.words)if(candidates.at(w).rect.contains(word.inkBox.center()))taken=true;
       if(taken)continue;
       if(word.matched){if(in)any=true;leaked+=outside;if(outside)who.append(QString("leak:%1:%2").arg(word.text).arg(outside));}
       else if(in){neighbour+=in;++neighbourWords;who.append(QString("nb:%1:%2").arg(word.text).arg(in));}
      }
      // A match recognition never found is "missed", not a leak of the cover.
      if(version==1){++expected;if(!any)++missed;}
      if(!any)leaked=-1;
      auto& t=totals[version];++t.cases;
      if(leaked>0){t.leaked+=leaked;++t.leakCases;}
      if(neighbour>0){t.neighbour+=neighbour;t.neighbourWords+=neighbourWords;++t.neighbourCases;}
      perLine.append(QJsonObject{{"line",l},{"leaked",leaked},{"neighbourInk",neighbour},{"neighbourWords",neighbourWords},{"who",who}});
     }
     rows.append(QJsonObject{{"font",family},{"px",px},{"theme",theme},{"code",versions[version]},{"lines",perLine}});
     if(!out.isEmpty()&&version==1){
      QImage shown=image;QPainter s(&shown);for(const auto& r:covers)s.fillRect(r,Qt::black);s.end();
      shown.save(QDir(out).filePath(QString("%1-%2-%3-new.png").arg(QString(family).replace(' ','_')).arg(px).arg(theme)));
      QImage before=image;QPainter b(&before);
      for(const auto& match:found){for(const auto& r:oldMarks(candidates,match,bounds))b.fillRect(r,Qt::black);}b.end();
      before.save(QDir(out).filePath(QString("%1-%2-%3-old.png").arg(QString(family).replace(' ','_')).arg(px).arg(theme)));
      image.save(QDir(out).filePath(QString("%1-%2-%3-source.png").arg(QString(family).replace(' ','_')).arg(px).arg(theme)));
     }
    }
   }
  }
 }
 QJsonObject summary{{"expectedMatches",expected},{"missedByRecognition",missed}};
 for(int v=0;v<versions.size();++v){const auto& t=totals[v];summary[versions[v]]=QJsonObject{{"lineCases",t.cases},{"casesLeaking",t.leakCases},{"leakedPixels",t.leaked},{"casesCoveringNeighbours",t.neighbourCases},{"neighbourWordsTouched",t.neighbourWords},{"neighbourInkPixels",t.neighbour}};}
 std::printf("%s\n",QJsonDocument(QJsonObject{{"summary",summary},{"rows",rows}}).toJson(QJsonDocument::Indented).constData());
 return 0;
}
