from pathlib import Path
import sys,time
sys.path.insert(0,'/home/patrick/work/svm1398/repo/tools/lab');import lab
root=Path('/home/patrick/work/svm1398/repo/work/lab-runs')
for k,x,y in [('n',640,327),('k',848,401)]:
 r=root/(k+'f');lab.pointer(r,x,y,1280,800,True);time.sleep(.2);lab.pointer(r,x,y,1280,800,False)
