#include "SettingsGuiFixture.h"
#include <QElapsedTimer>
class Log final:public QObject{public:QElapsedTimer t;QStringList lines;bool on=false;
 bool eventFilter(QObject* o,QEvent* e)override{if(on&&(e->type()==QEvent::LayoutRequest||e->type()==QEvent::Resize||e->type()==QEvent::Show||e->type()==QEvent::Hide)){auto* w=static_cast<QWidget*>(o);lines<<QString("%1ms %2 %3 h=%4 min=%5").arg(t.elapsed()).arg(o->property("probeName").toString()).arg(e->type()==QEvent::LayoutRequest?"LayoutRequest":e->type()==QEvent::Resize?"Resize":e->type()==QEvent::Show?"Show":"Hide").arg(w->height()).arg(w->minimumHeight());}return false;}};
class Probe:public SettingsGuiFixture {
 Q_OBJECT
private slots:
 void statusRowFollowsText(){
  QTemporaryDir dir;SettingsService service(dir.filePath("config.json"),[](auto,auto){return Error{};});
  QVERIFY(service.save(Settings::developmentTemplate(),{}));CredentialStore secrets;UiSessionFixture fixture(service,secrets);
  QJsonObject update;int minute=0;fixture.server.setUiDiagnostics([&]{return QJsonObject{{"update",update},{"trayAvailable",true}};});
  const QJsonObject build{{"version","26.1117.5114-nightly"},{"channel","nightly"},{"packageTarget","appimage"}};
  const auto set=[&](bool checking){update=QJsonObject{{"supported",true},{"build",build},{"channel","nightly"},{"check",true},{"checking",checking},
   {"result",QJsonObject{{"updateAvailable",true},{"latest","26.1118.5367-nightly"}}},{"checkedAt",QString("2026-11-19T19:%1:00Z").arg(minute,2,10,QChar('0'))},{"nextCheckAt",QString("2026-11-20T19:%1:00Z").arg(minute,2,10,QChar('0'))}};};
  set(false);fixture.session.refreshSnapshot();
  MainWindow window(fixture.session);const int w=qEnvironmentVariableIntValue("PROBE_WIDTH")?qEnvironmentVariableIntValue("PROBE_WIDTH"):1000;window.resize(w,qEnvironmentVariableIntValue("PROBE_HEIGHT")?qEnvironmentVariableIntValue("PROBE_HEIGHT"):900);window.navigate("settings");window.show();QVERIFY(putgd::test::waitForWindowExposed(&window));
  auto* label=window.findChild<QLabel*>("updateStatus");auto* button=window.findChild<QPushButton*>("checkForUpdatesNow");QVERIFY(label&&button);
  if(auto* scroll=qobject_cast<QScrollArea*>(label->parentWidget()->parentWidget()->parentWidget()->parentWidget()->parentWidget()->parentWidget()->parentWidget()))scroll->ensureWidgetVisible(label);
  Log log;log.t.start();label->setProperty("probeName","label");label->installEventFilter(&log);int depth=0;
  for(QWidget* p=label->parentWidget();p;p=p->parentWidget()){p->setProperty("probeName",QString("%1:%2[%3]").arg(depth++).arg(p->metaObject()->className(),p->objectName()));p->installEventFilter(&log);if(p->property("preferenceCard").toBool()||depth>9)break;}
  const auto dump=[&](const QString& tag){
   QStringList parts;parts<<QString("%1 label h=%2 hfw=%3 w=%4").arg(tag).arg(label->height()).arg(label->heightForWidth(label->width())).arg(label->width());
   for(QWidget* p=label->parentWidget();p;p=p->parentWidget()){parts<<QString("  %1 h=%2 min=%3 hfw=%4 laymin=%5 laygeom=%6").arg(p->property("probeName").toString()).arg(p->height()).arg(p->minimumHeight()).arg(p->layout()?p->layout()->totalHeightForWidth(p->width()):-1).arg(p->layout()?p->layout()->totalMinimumSize().height():-1).arg(p->layout()?p->layout()->geometry().height():-1);if(p->property("preferenceCard").toBool())break;}
   qInfo().noquote()<<parts.join("\n");
  };
  int bad=0;const int iterations=qEnvironmentVariableIntValue("PROBE_N")?qEnvironmentVariableIntValue("PROBE_N"):20;
  for(int i=0;i<iterations;++i){
   ++minute;const int delay=qEnvironmentVariableIntValue("PROBE_DELAY")+ (i*137)%400;fixture.client.replyDelayMs["update.check"]=delay;
   set(true);log.lines.clear();log.on=true;
   PUTGD_TRY_VERIFY(button->isEnabled());QTest::mouseClick(button,Qt::LeftButton);
   fixture.session.refreshSnapshot();
   QTimer::singleShot(delay/2,&window,[&]{set(false);});
   PUTGD_TRY_VERIFY(label->text().startsWith("put.gd")&&button->isEnabled());putgd::test::settle(300);log.on=false;
   const bool ok=label->height()>=label->heightForWidth(label->width());if(!ok)++bad;dump(QString("iter %1 delay %2 %3").arg(i).arg(delay).arg(ok?"ok":"CLIPPED"));
   if(!ok||qEnvironmentVariableIntValue("PROBE_LOG"))qInfo().noquote()<<log.lines.join("\n");
  }
  QCOMPARE(bad,0);
 }
};
QTEST_MAIN(Probe)
#include "test_settings_general.moc"
