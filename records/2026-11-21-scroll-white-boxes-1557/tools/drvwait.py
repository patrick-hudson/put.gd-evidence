# drvwait.py REPO: lab-only: with PUTGD_LAB_TEE_DIR set, the driver keeps the
# helper 40 s after the result before discarding it (discard kills it 2 s
# later), so the frame tee writes its queue.
import sys
p = sys.argv[1] + '/tests/fixtures/scroll_capture_driver.cpp'
s = open(p).read()
old = "        backend.discard(id);\n        QTimer::singleShot(1500, &app, [&] { app.exit(code); });"
assert s.count(old) == 1
s = s.replace(old, "        QTimer::singleShot(std::getenv(\"PUTGD_LAB_TEE_DIR\") ? 40000 : 0, &app, [&] {  // LAB ONLY (frame tee)\n            backend.discard(id);\n            QTimer::singleShot(1500, &app, [&] { app.exit(code); });\n        });")
if '#include <cstdlib>' not in s:
    s = s.replace('#include <cstdio>', '#include <cstdio>\n#include <cstdlib>', 1)
open(p, 'w').write(s)
print('driver wait patched')
