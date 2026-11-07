import json,pathlib,subprocess,os,time
root=pathlib.Path('/home/patrick/work/wc1255');os.chdir(root)
results=[]
for name,ref in [('linux','campaign/linux-final'),('s3','campaign/s3-contract'),('accessibility','campaign/shortcut-accessibility')]:
 subprocess.run(['git','checkout','--detach',ref],check=True)
 head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();row={'name':name,'head':head,'commands':[]};results.append(row)
 commands=[['cmake','--preset','dev'],['cmake','--build','--preset','dev','--parallel','3'],['python3','/home/patrick/work/wc-ctest.py']]
 if name=='s3':commands.append(['python3','tests/ci/test_s3_contract.py'])
 for index,command in enumerate(commands):
  log=root/(name+'-'+str(index)+'.log');started=time.monotonic()
  with log.open('w') as stream:r=subprocess.run(command,stdout=stream,stderr=subprocess.STDOUT,env=dict(os.environ,WC_RUN=name))
  row['commands'].append({'command':command,'exitCode':r.returncode,'seconds':round(time.monotonic()-started,2),'log':str(log)})
  (root/'campaign-results.json').write_text(json.dumps(results,indent=2))
  print(name,index,r.returncode,flush=True)
  if r.returncode and index<2:raise SystemExit(r.returncode)
