import accept as A,json,time,subprocess,sys
from pathlib import Path
P=A.P;L=A.L
try:
 profile=P/'profile-firefox'
 if profile.exists():profile.rename(P/(profile.name+'-'+str(time.time_ns())))
 L.browser_start('firefox');b,_=L.connect();b.navigate('https://en.wikipedia.org/wiki/Linux');time.sleep(6)
 # Old nightly has resume, but not the new autoScroll method.
 src=(Path(__file__).parent/'race.py').read_text().replace(",'driver':'user'","").replace("'scroll.autoScroll',{'id':sid,'on':True}","'scroll.resume',{'id':sid}")
 (P/'race-supported-alias.py').write_text(src)
 subprocess.run([sys.executable,str(P/'race-supported-alias.py')],check=True,env=dict(A.os.environ,PYTHONPATH=str(Path(__file__).parent)))
finally:L.browser_stop()
