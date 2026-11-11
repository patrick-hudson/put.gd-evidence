from pathlib import Path
import sys,json,re,hashlib,numpy as np
from PIL import Image
ns={};exec(Path("/home/patrick/work/svm1398/v2analyze.py").read_text().split("out=json.loads")[0],ns)
b=Path("/home/patrick/work/svm1398/v3evidence");all={}
for k in sys.argv[1]:
 out={}
 for d in sorted((b/k/"final/cases").iterdir()):
  if not (d/"result.json").exists():continue
  a=json.loads((d/"result.json").read_text());c=a.get("capture",{});f=d/"capture.png";n=d.name;v=None
  if f.exists() and not n.startswith("harness"):
   if n.startswith(("gtk","qt")):
    im=np.asarray(Image.open(f).convert("L")).astype(np.int16);part=im[:,:int(im.shape[1]*.6)];ink=np.abs(part-int(np.median(part)))>60;rows=ink.any(axis=1);change=np.diff(np.r_[False,rows,False].astype(int));starts=np.where(change==1)[0];ends=np.where(change==-1)[0];pitch=np.unique(np.diff(starts)).tolist();keys=[hashlib.sha1(np.packbits(ink[x:y]).tobytes()).hexdigest() for x,y in zip(starts,ends)];v={"bands":len(keys),"distinct":len(set(keys)),"pitch":pitch,"ok":len(keys)==1500 and len(set(keys))==1500 and len(pitch)==1,"height":len(rows)}
   else:
    exp=2000 if n=="cap-local" else 2400 if n=="postcap-local" else 24000 if n.startswith(("long","half-on","postcap")) else 12000 if n=="half-off" else 2000 if n=="cap" else None if n.startswith(("stop","user")) else 2400
    v=ns["ruler"](f,exp,first=12000 if n=="half-off" else None if n.startswith("stop") else 0,scale=1.25 if n=="fraction" else 1,codewidth=1280 if n in ("cap-local","postcap-local") else 640 if n=="fraction" else 960 if n.startswith(("long","half","stop","cap","postcap","user")) else 1280)
    if not v["ok"] and c.get("endReason") in ["lost_track","stopped"]:
     prefix=ns["ruler"](f,None,first=v.get("firstPixel",0),codewidth=960 if n.startswith(("long","half","stop","cap","postcap","user")) else 1280);v["exactPrefix"]=prefix["ok"]
  log=(d/"helper.log").read_text() if (d/"helper.log").exists() else ""
  out[n]={"state":c.get("state"),"end":c.get("endReason"),"error":a.get("error") or c.get("error"),"verify":v,"source":re.findall(r"scroll: source[^\n]*",log),"cadence":re.findall(r"scroll tap buffer: t=(\d+)",log)}
 all[k]=out
 (b/k/"analysis.json").write_text(json.dumps(out,indent=2))
 print(k,[(n,a["end"],a["verify"]) for n,a in out.items() if not n.startswith("harness")],flush=True)
(b/"analysis.json").write_text(json.dumps(all,indent=2))
