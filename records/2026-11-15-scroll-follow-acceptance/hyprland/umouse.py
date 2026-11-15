import subprocess,sys,shlex
import accept as A
sys.exit(subprocess.run([*A.SSH,shlex.join(["python3",A.GP+"/umouse-native.py"]) ]).returncode)
