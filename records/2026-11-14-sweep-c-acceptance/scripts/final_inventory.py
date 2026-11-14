import pathlib,subprocess,json,os,datetime
root=pathlib.Path('/home/patrick/work/sc1114')
def command(args):
 p=subprocess.run(args,text=True,capture_output=True);return {'exitCode':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
owned=[]
for p in pathlib.Path('/proc').iterdir():
 if not p.name.isdecimal() or int(p.name)==os.getpid():continue
 try:
  args=(p/'cmdline').read_bytes().split(b'\0');env=(p/'environ').read_bytes().split(b'\0')
  if any(str(root).encode() in a for a in args) or any(e.startswith(b'XDG_CONFIG_HOME=/tmp/scc1') for e in env):owned.append({'pid':int(p.name),'comm':(p/'comm').read_text().strip()})
 except OSError:pass
paths=[root,pathlib.Path('/tmp/scc1'),pathlib.Path('/tmp/sbr898847')]
print(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'package':command(['dpkg-query','-s','putgd']),'installedBuild':json.loads(subprocess.check_output(['/usr/bin/putgd','--version-json'],text=True)),'ownedProcesses':owned,'scratch':[{'path':str(p),'bytes':int(subprocess.check_output(['du','-sb',str(p)],text=True).split()[0])}for p in paths if p.exists()],'extension':'Not touched; Cinnamon X11 only','guestsBooted':0},indent=2))
