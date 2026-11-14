from pathlib import Path
import time
print('Scroll acceptance terminal: type the witness and press Enter.',flush=True)
s=input()
p=Path.home()/'work/s1520/a/terminal-received.txt';p.write_text(s+'\n')
print('Received: '+s,flush=True)
time.sleep(300)
