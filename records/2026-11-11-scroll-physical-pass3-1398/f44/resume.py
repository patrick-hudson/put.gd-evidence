import pass2,record_run,json,os,subprocess,time
P=pass2.P;e,desk=record_run.session_environment();old=json.loads((P/'env.json').read_text());old.update({k:v for k,v in e.items() if k not in ['XDG_RUNTIME_DIR','XDG_CONFIG_HOME','XDG_DATA_HOME','XDG_CACHE_HOME','XDG_STATE_HOME']});(P/'env.json').write_text(json.dumps(old));os.chmod(P/'env.json',0o600)
sock=P/'r/putgd/session.sock'
if sock.exists():sock.unlink()
p=subprocess.Popen(['putgd','--background'],env=old,stdout=open(P/'resident.log','a'),stderr=subprocess.STDOUT,start_new_session=True);(P/'resident.pid').write_text(str(p.pid));time.sleep(3)
print(pass2.rpc('desktop.setup.recheck'));print(pass2.rpc('scroll.capabilities'))
