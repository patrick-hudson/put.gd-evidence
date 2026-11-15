# Browser reference only, from the unchanged public Python page; no product capture.
import accept as A,time,json,sys
from pathlib import Path
P=A.P;L=A.L
try:
 profile=P/'profile-firefox'
 if profile.exists():profile.rename(P/(profile.name+'-'+str(time.time_ns())))
 L.browser_start('firefox');b,_=L.connect();b.navigate('https://en.wikipedia.org/wiki/Linux');time.sleep(6);L.wait_loaded(b,25)
 (P/'wiki-reference-info.json').write_text(json.dumps(b.js(L.INFO),indent=1));b.shot_full(P/'wiki-reference.png')
 b.navigate('https://docs.python.org/3/library/stdtypes.html');time.sleep(6);L.wait_loaded(b,25)
 (P/'python-reference-info.json').write_text(json.dumps(b.js(L.INFO),indent=1));b.shot_full(P/'python-reference.png')
finally:L.browser_stop()
