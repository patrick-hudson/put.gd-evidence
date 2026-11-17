import accept as A,os,subprocess,time,importlib.util
from pathlib import Path
P=A.P;os.environ['LAB_TAG']='B4-1'
spec=importlib.util.spec_from_file_location('pages',P/'pages-relative.py');M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M);L=M.L;S=M.S
profile=P/'profile-firefox'
if profile.exists():profile.rename(P/(profile.name+'-retry-'+str(time.time_ns())))
mouse=subprocess.Popen(['sudo','-n','python3',str(P/'umouse.py')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True);assert mouse.stdout.readline().startswith('ready')
def wheel(s):mouse.stdin.write(s+'\n');mouse.stdin.flush()
try:L.browser_start('firefox');S.run('firefox','github','auto',wheel)
finally:L.browser_stop();wheel('q');mouse.wait(5)
