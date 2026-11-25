import json,sys
from pathlib import Path
from types import SimpleNamespace
from accept import player,rr
import desktop_lock
desktop_lock.refuse_unless_held('ffmpeg91 playback')
d=SimpleNamespace(run=Path(sys.argv[1]).resolve(),args=SimpleNamespace(vnc_port=int(sys.argv[2])),env=rr.session_environment()[0])
d.env['SDL_AUDIODRIVER']='dummy'
report={fmt:player(d,d.run/'out'/f'{fmt}.{fmt}') for fmt in ['mp4','webm']}
(d.run/'player-replay.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
sys.exit(not all(row['wasPlayingAfter2s'] and row['exit']==0 and any(f.get('ok') for f in row['wallFrames']) for row in report.values()))
