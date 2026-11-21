# teedrain.py REPO: lab-only, on top of labtee2+labtee_fix: the tee writes every
# queued frame before the tracker finishes (the helper exits soon after and
# lost the last ~100 frames, written as empty files).
import sys
p = sys.argv[1] + '/src/record/ScrollSession.cpp'
s = open(p).read()
def rep(old, new):
    global s
    assert s.count(old) == 1, old
    s = s.replace(old, new)
rep("    std::deque<std::pair<QImage, QString>> q;", "    std::deque<std::pair<QImage, QString>> q;\n    int busy = 0;\n    std::condition_variable idle;")
rep("""            auto item = std::move(q.front());
            q.pop_front();
            l.unlock();
            item.first.save(item.second, "PNG", 90);""",
    """            auto item = std::move(q.front());
            q.pop_front();
            ++busy;
            l.unlock();
            item.first.save(item.second, "PNG", 90);
            l.lock();
            --busy;
            idle.notify_all();""")
rep("    void newRun() {", """    void drain() {
        std::unique_lock<std::mutex> l(m);
        idle.wait(l, [&] { return q.empty() && busy == 0; });
    }
    void newRun() {""")
rep("    const auto totals = tracker_->finish();", "    if (LabTee* tee = labTee()) tee->drain();\n    const auto totals = tracker_->finish();")
open(p, 'w').write(s)
print('drain patched')
