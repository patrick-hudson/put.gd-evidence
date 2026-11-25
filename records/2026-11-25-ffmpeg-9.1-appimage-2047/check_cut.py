from pathlib import Path
import json,hashlib,subprocess as sp,statistics
from PIL import Image,ImageChops,ImageStat
root=Path(__file__).parent
for host in ['aurora-amd','f44','m74']:
    p=root/host; d=json.loads((p/'receipt.json').read_text()); clip=p/'clips'; e=d['editedReview']['edit']; cut=e['cuts'][0]; fps=30
    def read(kind):
        f=clip/(kind+'.mp4'); stats=d['stats'][kind]; assert hashlib.sha256(f.read_bytes()).hexdigest()==stats['sha256']
        w,h=stats['size']; x,y,ww,hh=[round(v*s) for v,s in zip([1088,540,256,216],[w/1920,h/1080,w/1920,h/1080])]
        raw=sp.run(['ffmpeg','-hide_banner','-nostdin','-v','error','-threads','2','-xerror','-i',str(f),'-map','0:v:0','-vf',f'crop={ww}:{hh}:{x}:{y},scale=128:108:flags=area,format=gray','-fps_mode','passthrough','-f','rawvideo','-'],capture_output=True,check=True).stdout
        n=128*108; assert len(raw)%n==0
        return [Image.frombytes('L',(128,108),raw[i:i+n]) for i in range(0,len(raw),n)]
    orig,edited=read('mp4'),read('edited'); start=round(e['trimStart']*fps/1e6); cs=round(cut['start']*fps/1e6); ce=round(cut['end']*fps/1e6); seam=cs-start
    def diff(a,b): return ImageStat.Stat(ImageChops.difference(a,b)).mean[0]
    rows=[]
    for idx in [15,30,seam-5,seam-2,seam-1,seam,seam+1,seam+2,seam+5,seam+15,seam+30,seam+60]:
        mapped=start+idx+(ce-cs if idx>=seam else 0); wrong=start+idx
        pairs=[(diff(edited[idx],orig[i]),i) for i in range(mapped-1,mapped+2)]
        score,best=min(pairs); wrongscore=min(diff(edited[idx],orig[i]) for i in range(wrong-1,wrong+2))
        rows.append(dict(outputFrame=idx,expectedSourceFrame=mapped,bestSourceFrame=best,matchedBallDifference=score,uncutBallDifference=wrongscore))
    post=[r for r in rows if r['outputFrame']>=seam]; result={'host':host,'seamOutputFrame':seam,'firstKeptSourceFrameAfterCut':ce,'firstTrimFrame':start,'rows':rows,'postCutMeanKeptDifference':statistics.mean(r['matchedBallDifference'] for r in post),'postCutMeanUncutDifference':statistics.mean(r['uncutBallDifference'] for r in post)}
    print(result['host'],result['postCutMeanKeptDifference'],result['postCutMeanUncutDifference'])
    (p/'cut-content-check.json').write_text(json.dumps(result,indent=2)+'\n')
