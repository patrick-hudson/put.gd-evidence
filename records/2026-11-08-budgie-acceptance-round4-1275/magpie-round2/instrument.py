# Diagnostic copy of Magpie 58a0d7a: log what the event translation produces.
# MAGPIE_PROBE_FIX=1 additionally names keysyms that have no text, and drops the "none" prefix.
p='src/mir/qmirkeyboardevent.cpp'; s=open(p).read()
s=s.replace('#include <qkeysequence.h>\n','#include <qkeysequence.h>\n#include <QDebug>\n#include <cstdlib>\n',1)
old='''  xkb_keysym_to_utf8(miral::toolkit::mir_keyboard_event_keysym(event), buf, sizeof(buf));
  auto key = QString::fromUtf8(buf);
'''
new='''  auto rawSym = miral::toolkit::mir_keyboard_event_keysym(event);
  int  written = xkb_keysym_to_utf8(rawSym, buf, sizeof(buf));
  auto key = QString::fromUtf8(buf);
  char symName[64] = {0};
  xkb_keysym_get_name(rawSym, symName, sizeof(symName));
  auto const unfixed = key;
  bool const fix = std::getenv("MAGPIE_PROBE_FIX") != nullptr;
  if (fix && (written <= 0 || key.isEmpty() || key.at(0).unicode() < 0x20 || key.at(0).unicode() == 0x7f)) key = QString::fromLatin1(symName);
'''
assert old in s; s=s.replace(old,new,1)
old='''  m_sequence = QKeySequence::fromString(fullKeycombo);
'''
new='''  if (fix && qMods == QMirInputEventModifier::Modifiers{}) fullKeycombo = key;
  m_sequence = QKeySequence::fromString(fullKeycombo);
  qDebug().nospace() << "PROBE keysym=" << symName << " utf8_bytes=" << written << " text=" << unfixed.toUtf8().toHex() << " combo=" << fullKeycombo << " -> sequence=" << m_sequence.toString() << " count=" << m_sequence.count() << " qkey=" << Qt::hex << (m_sequence.count() ? int(m_sequence[0].toCombined()) : -1);
'''
assert old in s; s=s.replace(old,new,1)
open(p,'w').write(s)
