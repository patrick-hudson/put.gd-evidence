handle all nostop noprint pass
set pagination off
set confirm off
set print thread-events off
set debuginfod enabled off
set breakpoint pending on
python
import sys
class Acq(gdb.Breakpoint):
    def stop(self):
        print("ACQUIRE id=%s" % gdb.parse_and_eval("id"), flush=True)
        return False
class Adv(gdb.Breakpoint):
    def stop(self):
        print("ADVANCE", flush=True)
        return False
Acq("mir::compositor::MultiMonitorArbiter::compositor_acquire")
Adv("multi_monitor_arbiter.cpp:101")
end
run
