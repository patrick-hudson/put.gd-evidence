import pathlib,sys,subprocess,shlex
sys.path.insert(0,'/tmp/b1364');from control import G
E=pathlib.Path('/home/patrick/work/putgd-evidence/2026-11-10-recording-1364-budgie-final-visible');E.mkdir(mode=0o700,exist_ok=True);(E/'runs').mkdir(exist_ok=True);(E/'drivers').mkdir(exist_ok=True);(E/'identity').mkdir(exist_ok=True)
subprocess.run(['rsync','-aH','--exclude=appdir-*','--exclude=cache','--exclude=config','--exclude=data','--exclude=archive','--exclude=*.sock','--exclude=running.*','-e',shlex.join(G[:-1]),G[-1]+':/home/lab/b1364v/r/',str(E/'runs')],check=True)
for name in ('visible.json','audio.json','build-version.txt','socket-preflight.json','default-sink.txt','default-source.txt','sources-before.txt','labwc-version.txt','budgie-version.txt'):
 p=subprocess.run(G+['cat /home/lab/b1364v/'+name],capture_output=True,check=True);(E/name).write_bytes(p.stdout)
