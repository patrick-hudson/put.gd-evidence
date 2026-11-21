# teedrain2.py REPO: fix teedrain's call site (finishTracker comes before the tee block).
import re, sys
p = sys.argv[1] + '/src/record/ScrollSession.cpp'
s = open(p).read()
old = "    if (LabTee* tee = labTee()) tee->drain();\n    const auto totals = tracker_->finish();"
assert s.count(old) == 1
s = s.replace(old, "    labTeeDrain();\n    const auto totals = tracker_->finish();")
m = re.search(r'\n[^\n]*ScrollSession::finishTracker\(\)', s)
s = s[:m.start()] + '\nstatic void labTeeDrain();  // LAB ONLY (frame tee)' + s[m.start():]
end = '// ---- end LAB ONLY ----'
assert s.count(end) == 1
s = s.replace(end, 'static void labTeeDrain() {\n    if (LabTee* tee = labTee()) tee->drain();\n}\n' + end)
open(p, 'w').write(s)
print('drain2 patched')
