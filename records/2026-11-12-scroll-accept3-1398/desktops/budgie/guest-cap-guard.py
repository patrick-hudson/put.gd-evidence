from pathlib import Path
P=Path('/home/lab/work/s3a')
f=P/'pass2.py';s=f.read_text();s=s.replace('def rpc(m,p={}):','def rpc(m,p={}):\n if m=="scroll.prepare":assert p.get("maxHeight",30000)<=30000,"d69 cap preflight"');s=s.replace(' out=P/name;out.mkdir();',' maxh=min(maxh,30000) if maxh else None\n out=P/name;out.mkdir();');f.write_text(s)
for n in ['notices.py','minimap-repeat.py','browsercases.py','capmore.py']:
 f=P/n;f.write_text(f.read_text().replace('40000','30000').replace('60000','30000'))
print('guest capture policy guard installed before remaining stages')
