import sys,subprocess,json,time,os
from pathlib import Path
p=Path.home()/'putgd-lab';case=sys.argv[1]
cmd=['python3',str(p/'scroll_run_vm.py'),'--out',str(p/case),'--package','/home/lab/ci.AppImage','--rect','0,0,1280,800','--rows','60','--format','fixture','--code-width','1280','--png-root',str(p/'archive'),'--png-root',str(p/'data')]
if os.uname().nodename=='omarchy-lab':
 cmd[cmd.index('--rect')+1]='0,0,608,800';cmd[cmd.index('--code-width')+1]='608'
if case.startswith('cancel'):cmd+=['--control','cancel','--after','1']
elif case.startswith('stop'):cmd+=['--control','stop','--after','1','--expect-end','stopped']
else:cmd+=['--max-height','5000']
subprocess.run(cmd,stdout=open(p/(case+'-console.log'),'w'),stderr=subprocess.STDOUT)
print((p/(case+'-console.log')).read_text())
