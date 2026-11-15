from pathlib import Path
import json,re,sys,hashlib
root=Path(sys.argv[1]);rows=[]
for d in sorted((root/'runs').iterdir()):
 if 'incomplete' in d.name or not (d/'result.json').exists():continue
 r=json.loads((d/'result.json').read_text());c=r.get('capture') or {};s=(d/'helper.log').read_text() if (d/'helper.log').exists() else ''
 fps=[float(x) for x in re.findall(r'scroll: source \d+ frames in \d+ ms \(([0-9.]+) per second\)',s)]
 fresh=[line for line in s.splitlines() if 'scroll fresh frame:' in line or "Done's fresh frame" in line]
 elapsed=c.get('elapsedMs',(c.get('stats') or {}).get('elapsedMs'));height=c.get('height')
 expected=(c.get('result') or {}).get('sha256');actual=hashlib.sha256((d/'capture.png').read_bytes()).hexdigest() if (d/'capture.png').exists() else None
 if expected and actual:assert expected==actual,(d.name,expected,actual)
 rows.append({'captureSha256':actual,'reportedSha256':expected,'sha256Matches':expected==actual if expected and actual else None,'run':d.name,'end':c.get('endReason'),'reachedEnd':c.get('reachedEnd'),'truncated':c.get('truncated'),'scrolledBy':c.get('scrolledBy'),'placed':c.get('framesPlaced'),'skipped':c.get('framesSkipped'),'fps':fps,'injectionLines':len(re.findall(r'scroll inject:',s)),'wheelStepLines':len(re.findall(r'scroll step:',s)),'freshFrameLines':fresh,'rowsAtDone':c.get('rowsAtDone',(c.get('stats') or {}).get('rowsAtDone')),'hiddenCells':c.get('hiddenCells'),'hiddenRows':c.get('hiddenRows'),'elapsedMs':elapsed,'height':height,'secondsPer10000px':round(elapsed/1000*10000/height,3) if elapsed and height else None,'referenceError':r.get('referenceError')})
out=root/'protocol-checks.json';out.write_text(json.dumps(rows,indent=1));print(json.dumps(rows,indent=1))
