import sys,subprocess,shlex,pathlib
sys.path.insert(0,'/tmp/b1364');from control import G,H
E=pathlib.Path('/home/patrick/work/putgd-evidence/2026-11-10-recording-1364-budgie-followup');(E/'runs').mkdir(exist_ok=True);(E/'identity').mkdir(exist_ok=True);(E/'drivers').mkdir(exist_ok=True)
subprocess.run(['rsync','-aH','--exclude=appdir-*','--exclude=cache','--exclude=config','--exclude=data','--exclude=archive','--exclude=*.sock','--exclude=running.*','-e',shlex.join(G[:-1]),G[-1]+':/home/lab/b1364f/r/',str(E/'runs/')],check=True)
for name in ('matrix.json','motion.json','ring-effect.json','shared-audio.json','motion-audio.json','g-new-before.xml','g-new-after.xml','build-version.txt','socket-preflight.json','default-sink.txt','default-source.txt','sources-before.txt'):
 p=subprocess.run(G+['cat /home/lab/b1364f/'+name],capture_output=True,check=True);(E/name).write_bytes(p.stdout)
for tag in ('g-new-driver','g-retained'):
 dest=E/'runs'/tag/'captures';dest.mkdir(exist_ok=True)
 subprocess.run(['rsync','-a','-e',shlex.join(G[:-1]),G[-1]+':/home/lab/b1364f/r/'+tag+'/archive/images/',str(dest)+'/'],check=True)
