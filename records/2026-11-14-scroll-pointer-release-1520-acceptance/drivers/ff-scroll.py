from pathlib import Path
import ctypes,json,struct,os,stat
root=Path.home()/'work/s1520/ff';lib=ctypes.CDLL('liblz4.so.1');lib.LZ4_decompress_safe.argtypes=[ctypes.c_char_p,ctypes.c_void_p,ctypes.c_int,ctypes.c_int]
out=[]
for p in root.rglob('*jsonlz4'):
 if not p.is_file():continue
 s=p.lstat()
 if not stat.S_ISREG(s.st_mode) or s.st_uid!=os.getuid():continue
 try:
  b=p.read_bytes()
  if not b.startswith(b'mozLz40\0'):continue
  n=struct.unpack('<I',b[8:12])[0]
  if n>50_000_000:continue
  buf=ctypes.create_string_buffer(n);got=lib.LZ4_decompress_safe(b[12:],buf,len(b)-12,n)
  if got<0:continue
  v=json.loads(buf.raw[:got])
  def walk(x):
   if isinstance(x,dict):
    entries=x.get('entries',[])
    if isinstance(entries,list) and entries:
     idx=x.get('index',len(entries))-1
     if isinstance(idx,int) and 0<=idx<len(entries):
      entry=entries[idx]
      if isinstance(entry,dict) and entry.get('url','').split('#')[0]=='https://en.wikipedia.org/wiki/Linux':out.append({'file':str(p.relative_to(root)),'scroll':entry.get('scroll'),'index':x.get('index'),'tabScroll':x.get('scroll'),'lastAccessed':x.get('lastAccessed')})
    for child in x.values():walk(child)
   elif isinstance(x,list):
    for child in x:walk(child)
  walk(v)
 except (ValueError,OSError):pass
print(json.dumps(out,indent=2))
