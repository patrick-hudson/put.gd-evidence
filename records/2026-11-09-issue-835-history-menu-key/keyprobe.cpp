// LD_PRELOAD event witness for issue #835. It logs what Qt really delivers;
// it changes nothing and never accepts or filters an event.
#include <QAction>
#include <QApplication>
#include <QClipboard>
#include <QTimer>
#include <QContextMenuEvent>
#include <QCoreApplication>
#include <QDateTime>
#include <QFile>
#include <QGuiApplication>
#include <QKeyEvent>
#include <QMenu>
#include <QTextStream>
#include <QWidget>
#include <QWindow>
#include <unistd.h>

namespace {
QString name(QObject* o) {
  if (!o) return "null";
  return QString("%1(%2)").arg(o->metaObject()->className(), o->objectName());
}
class Probe : public QObject {
 public:
  explicit Probe(const QString& path, QObject* parent) : QObject(parent), file(path) { file.open(QIODevice::WriteOnly | QIODevice::Append | QIODevice::Text | QIODevice::Unbuffered); }
  bool eventFilter(QObject* o, QEvent* e) override {
    QString line;
    switch (e->type()) {
      case QEvent::KeyPress:
      case QEvent::KeyRelease:
      case QEvent::ShortcutOverride: {
        auto* k = static_cast<QKeyEvent*>(e);
        // Only the keys under test: Menu, XF86MenuKB as Qt sees it, F10.
        if (k->key() != Qt::Key_Menu && k->key() != Qt::Key_F10) return false;
        line = QString("%1 key=0x%2 mods=0x%3 scan=%4 vkey=0x%5 spontaneous=%6").arg(e->type() == QEvent::KeyPress ? "KeyPress" : e->type() == QEvent::KeyRelease ? "KeyRelease" : "ShortcutOverride").arg(k->key(), 0, 16).arg(int(k->modifiers()), 0, 16).arg(k->nativeScanCode()).arg(k->nativeVirtualKey(), 0, 16).arg(e->spontaneous());
        break;
      }
      case QEvent::Shortcut: {
        auto* s = static_cast<QShortcutEvent*>(e);
        line = QString("Shortcut seq=%1 ambiguous=%2").arg(s->key().toString()).arg(s->isAmbiguous());
        break;
      }
      case QEvent::ContextMenu: {
        auto* c = static_cast<QContextMenuEvent*>(e);
        line = QString("ContextMenu reason=%1 pos=%2,%3 global=%4,%5 spontaneous=%6").arg(int(c->reason())).arg(c->x()).arg(c->y()).arg(c->globalX()).arg(c->globalY()).arg(e->spontaneous());
        break;
      }
      case QEvent::Show:
      case QEvent::Hide:
        if (!qobject_cast<QMenu*>(o)) return false;
        line = e->type() == QEvent::Show ? "MenuShow" : "MenuHide";
        break;
      default:
        return false;
    }
    QTextStream out(&file);
    out << QDateTime::currentMSecsSinceEpoch() << " " << name(o) << " " << line << " focus=" << name(QApplication::focusWidget()) << " popup=" << name(QApplication::activePopupWidget()) << " focusWindow=" << name(QGuiApplication::focusWindow()) << "\n";
    return false;
  }
  QFile file;
};
void install() {
  if (!qobject_cast<QApplication*>(QCoreApplication::instance())) return;
  const QString dir = qEnvironmentVariable("PUTGD_KEY_PROBE_DIR", "/tmp");
  auto* probe = new Probe(QString("%1/keyprobe-%2.log").arg(dir).arg(getpid()), QCoreApplication::instance());
  QCoreApplication::instance()->installEventFilter(probe);
  QTimer::singleShot(0, probe, [probe] {
    QObject::connect(QGuiApplication::clipboard(), &QClipboard::dataChanged, probe, [probe] {
      QTextStream out(&probe->file);
      out << QDateTime::currentMSecsSinceEpoch() << " Clipboard " << QGuiApplication::clipboard()->text().simplified().left(1500) << "\n";
    });
  });
}
Q_COREAPP_STARTUP_FUNCTION(install)
}  // namespace
