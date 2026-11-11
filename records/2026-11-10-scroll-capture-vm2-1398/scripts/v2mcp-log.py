from pathlib import Path
import json,re,sys
base=Path('/home/patrick/work/svm1398/v2evidence')
for k in sys.argv[1]:
 p=base/k/'final';d=p/'cases/mcp';r=json.loads((d/'result.json').read_text())['capture'];text=(p/'helper.log').read_text();parts=re.split(r'(?m)(?=^.*scroll command prepare$)',text)
 good=[s for s in parts if 'scroll: capturing 0,0 1280x800 ' in s and ('ended EndOfContent, '+str(r['height'])+' rows' in s or 'ended LostTrack, '+str(r['height'])+' rows' in s)]
 if good:(d/'helper.log').write_text(good[-1]);print(k,re.findall(r'scroll: source[^\n]*',good[-1]))
