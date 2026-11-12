import fix6 as f,subprocess
f.resize_case('timer-resize','resize_window_fixture.py',1)
for args in [['timer-oracle-steady.py'],['switch-oracle.py',str(f.P)],['verify-cancel-ui.py'],['payload-proof.py']]:subprocess.run(['python3',str(f.P/args[0]),*args[1:]],check=False)
