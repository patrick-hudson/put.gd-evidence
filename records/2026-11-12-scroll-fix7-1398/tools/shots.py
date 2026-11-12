# shots.py NAME SECONDS : screenshots of the whole screen as fast as they come, with the time in the name, from the
# moment the helper's log grows (a capture begins) for SECONDS (lab: what the screen showed during a capture)
import sys, time
sys.path.insert(0, '/home/patrick/work/sf7')
import live7
out = live7.P / 'shots' / sys.argv[1]
out.mkdir(parents=True)
log = live7.P / 'helper.log'
size = log.stat().st_size if log.exists() else 0
limit = time.time() + 240
while time.time() < limit and (log.stat().st_size if log.exists() else 0) == size:
    time.sleep(0.05)
end = time.time() + float(sys.argv[2])
while time.time() < end:
    t = time.time()
    live7.screen_png(out / ('s-%s-%03d.png' % (time.strftime('%H%M%S', time.localtime(t)), int(t * 1000) % 1000)))
