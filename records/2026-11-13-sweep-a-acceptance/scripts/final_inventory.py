#!/usr/bin/env python3
import json,os,pathlib,subprocess,sys
host=sys.argv[1]; root=pathlib.Path('/home/patrick/work/sa1113')
names={'m74':['sam1','sam2','sam3','sac1','sac2','sac3','sax1','sab1','sab2','sad1','sad2','sad3','sarbar1','sas1','sat1','sat2','sat3','satn1','sau1','sau2'],'k72':['sakm1','sakm2','sakx1','sakb2','sakb3','sakb4','sakb5','sakoff1','sakc1','sakc2','sakbar1','saks1','sakt1','sakt2','saku1','sakrace1'],'f44':[]}[host]
paths=[root]+[pathlib.Path('/tmp')/n for n in names]; runtimes=set()
for f in root.glob('*.log'):
 for l in f.read_text(errors='replace').splitlines()[:3]:
  if l.startswith('{"socketPath"'):
   try: runtimes.add(pathlib.Path(json.loads(l)['socketPath']).parents[1] if l.find('session.sock')>=0 else pathlib.Path(json.loads(l)['socketPath']).parent)
   except (ValueError,KeyError):pass
paths+=sorted(runtimes)
scratch=[]
for p in paths:
 if p.is_dir():
  size=subprocess.check_output(['du','-sb','--',str(p)],text=True).split()[0];scratch.append({'path':str(p),'apparentBytes':int(size),'remainingSockets':[str(v) for v in p.glob('putgd/*.sock')] if p in runtimes else []})
processes=[]
for p in pathlib.Path('/proc').iterdir():
 if not p.name.isdecimal(): continue
 try:
  comm=(p/'comm').read_text().strip()
  if p.stat().st_uid==os.getuid() and (comm.startswith('putgd') or comm.startswith('gst-launch')): processes.append({'pid':int(p.name),'comm':comm})
 except (OSError,PermissionError):pass
q=['dpkg-query','-W','-f=${Status} ${Version}\n','putgd'] if host!='f44' else ['rpm','-q','putgd']
p=subprocess.run(q,capture_output=True,text=True)
print(json.dumps({'host':host,'packageState':p.stdout.strip(),'putgdAndGstreamerProcesses':processes,'scratch':scratch,'extensionTouched':False},indent=2))
