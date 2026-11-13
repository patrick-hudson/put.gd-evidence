from pathlib import Path
import sys
p=Path(sys.argv[1])/'tools/lab/cover_player.py'
s=p.read_text()
old="""description = ('videotestsrc is-live=true pattern=%s horizontal-speed=6 '
                       '! video/x-raw,width=%d,height=%d,framerate=30/1 ! videoconvert ! gtksink name=video' % (PATTERN, width, height))"""
new="""description = ('compositor name=m sink_1::alpha=0.7 ! videoconvert ! gtksink name=video '
                       'videotestsrc is-live=true pattern=%s horizontal-speed=6 '
                       '! video/x-raw,width=%d,height=%d,framerate=30/1 ! m.sink_0 '
                       'videotestsrc is-live=true pattern=ball '
                       '! video/x-raw,width=%d,height=%d,framerate=30/1 ! m.sink_1' % (PATTERN, width, height, width, height))"""
assert old in s
p.write_text(s.replace(old,new))
