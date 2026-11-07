import json, os, pathlib, subprocess, tempfile
with tempfile.TemporaryDirectory(prefix='c',dir='/tmp') as tmp:
 registry=json.loads(subprocess.check_output(['ctest','--preset','dev','--show-only=json-v1']))
 names={'test_'+t['name'] for t in registry['tests']}
 names.update(pathlib.Path(a).name for t in registry['tests'] for a in t.get('command',[]) if pathlib.Path(a).name.startswith('test_'))
 paths=[str(pathlib.Path(tmp)/(n+'-XXXXXX')/'runtime/putgd/session.sock') for n in sorted(names)]
 paths += [tmp+'/putgd mcp socket XXXXXXXX/session socket','/tmp/.X11-unix/X65535','/tmp/dbus-XXXXXXXXXX']
 report=subprocess.check_output(['python3','tools/diagnostics/check_socket_paths.py','--socket',*paths])
 pathlib.Path('socket-preflight-'+os.environ['WC_RUN']+'.json').write_bytes(report)
 environment=dict(os.environ,TMPDIR=tmp)
 environment.pop('QT_QPA_PLATFORM',None)
 result=subprocess.run(['ctest','--preset','dev','--parallel','6'],env=environment)
 raise SystemExit(result.returncode)
