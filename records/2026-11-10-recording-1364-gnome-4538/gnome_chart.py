import cairo,json,math
from pathlib import Path
base=Path.home()/'work/s1364s2';rows=[]
for case,label,color in [('mic','Microphone',(0.13,.36,.68)),('mixed','Microphone + system',(.55,.25,.62))]:
 for r in json.loads((base/'runs'/case/'results.json').read_text())['rounds']:
  c=r['clips']['export'];rows.append((label+' / '+r['format'].upper(),c['offsetsMs'],c['medianMs'],color))
sys=json.loads((base/'runs/system-compare/results.json').read_text())
for fmt in ['mp4','webm']:
 vals=[r['clips']['export']['medianMs'] for r in sys['rounds'] if r['build']=='nightly' and r['format']==fmt]
 rows.append(('Nightly system / '+fmt.upper(),vals,None,(.25,.28,.31)))
surf=cairo.ImageSurface(cairo.FORMAT_ARGB32,1050,620);c=cairo.Context(surf);c.set_source_rgb(1,1,1);c.paint()
def text(x,y,t,size=17,color=(.15,.17,.20),bold=False):
 c.set_source_rgb(*color);c.select_font_face('Sans',cairo.FONT_SLANT_NORMAL,cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL);c.set_font_size(size);c.move_to(x,y);c.show_text(t)
def X(v):return 285+(v+60)*3.1
def line(x,y,x2,y2,col,width=1):c.set_source_rgb(*col);c.set_line_width(width);c.move_to(x,y);c.line_to(x2,y2);c.stroke()
text(30,38,'GNOME: tone against the visible marker',27,bold=True)
text(30,69,'Physical f44 · installed RPM build 4538 · CI 42774290115 · product cccf91a50',16)
text(30,95,'All microphone and mixed clips include a 3 s pause. Positive values mean audio is late.',16)
top,bottom=140,482
c.set_source_rgb(.96,.97,.97);c.rectangle(X(-45),top,X(125)-X(-45),bottom-top);c.fill()
c.set_source_rgb(.86,.94,.90);c.rectangle(X(-33.333),top,X(33.333)-X(-33.333),bottom-top);c.fill()
for v in [-45,0,33.333,125]:line(X(v),top,X(v),bottom,(.65,.70,.70),1)
for i,(label,points,median,col) in enumerate(rows):
 y=170+i*55;text(22,y+6,label,17,bold=True)
 for j,p in enumerate(points):
  c.set_source_rgba(*col,.45);c.arc(X(p),y+((j%5)-2)*2.5,3.5,0,2*math.pi);c.fill()
 if median is not None:
  c.set_source_rgb(*col);c.move_to(X(median),y-9);c.line_to(X(median)+9,y);c.line_to(X(median),y+9);c.line_to(X(median)-9,y);c.close_path();c.fill();value=f'{median:+.1f} ms'
 else:
  line(X(min(points)),y,X(max(points)),y,col,2);value='/'.join(f'{v:+.1f}' for v in points)
 text(900,y+6,value,16,color=col)
for v in [-50,0,50,100,150]:line(X(v),bottom,X(v),bottom+5,(.35,.38,.40));text(X(v)-16,bottom+26,str(v),16)
text(430,540,'Audio minus picture (ms)',17,bold=True)
text(30,575,'Green: one-frame median target (±33.3 ms). Grey: required median bound (−45 to +125 ms).',16)
text(30,600,'Small dots: marker pairs. Diamonds: run medians. Nightly rows: three alternating control runs.',16)
surf.write_to_png(str(base/'pictures/gnome-alignment.png'))
