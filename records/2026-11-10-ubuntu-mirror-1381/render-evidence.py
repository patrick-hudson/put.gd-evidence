from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import re
root=Path('evidence')
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf',19)
large=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',29)
blocks=[]
blocks.append(('BEFORE: HEAD 200 retained the slow mirror | cdac6e4b3 / run 42737959530 attempt 1', [
 'sanitizers: Ubuntu mirrors reachable: us.archive.ubuntu.com ...',
 'sanitizers: Fetched 27.2 MB in 6min 22s (71.1 kB/s)',
 'sanitizers: Need to get 514 MB of archives. [dependency step timed out before tests]',
 'Original timed-out APT scenario not replayed; throttled HTTP-200 test fails before / passes after.']))
blocks.append(('INTERMEDIATE: fast metadata hid slow package payloads | 010480922 / run 42745955621', [
 'Linux 24.04: Azure index sample = 35,029,000 B/s; metadata fetched at 12.4 MB/s',
 'Linux 24.04: package transfers continued for 20 minutes, then the dependency step timed out.',
 'Correction: probe base noble libc6 .deb payload, with the same 2 MiB / 3-second bounds.']))
for name, filename in [('AFTER: Linux 24.04','linux24'),('AFTER: Linux 26.04','linux26'),('AFTER: Sanitizers','sanitizers'),('AFTER: Package Ubuntu 26.04 (warm snapshot)','package26')]:
 lines=(root/f'{filename}.log').read_text().splitlines()
 selected=[re.sub(r'^\S+Z ', '',s) for s in lines if 'Ubuntu mirror throughput:' in s][:4]
 selected += [re.sub(r'^\S+Z ', '',s) for s in lines if 'Fetched ' in s or 'Need to get ' in s][:(6 if filename == 'package26' else 3)]
 blocks.append((name,selected))
height=130+sum(65+len(lines)*29 for _,lines in blocks)
im=Image.new('RGB',(1800,height),'#131820');d=ImageDraw.Draw(im)
d.text((30,20),'Ubuntu mirror throughput: real CI log capture',font=large,fill='white')
d.text((30,66),'PR #1382 | head 1fb761600756 | run 42748578866 | bounded GET: 2 MiB / 3 seconds per mirror',font=font,fill='#aab4c5')
y=115
for i,(title,lines) in enumerate(blocks):
 h=55+len(lines)*29
 color='#ecaa61' if i<2 else '#67d8b0'
 d.rounded_rectangle((20,y,1780,y+h),8,outline=color,width=3)
 d.text((36,y+10),title,font=font,fill=color)
 for k,line in enumerate(lines):d.text((36,y+45+k*29),line,font=font,fill='#e0e7ef')
 y+=h+10
im.save(root/'ci-log-capture.png')
