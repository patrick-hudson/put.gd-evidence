import json,pathlib
E=pathlib.Path('/home/patrick/work/putgd-evidence/2026-11-10-recording-1364-budgie-final-visible');rows=json.loads((E/'summary.json').read_text())['order']
x=lambda v:80+(v+45)*3.2
svg=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 700 230" role="img" aria-label="Eight visible-bar run medians, all within minus45 to plus125 milliseconds">']
svg+=['<text x="8" y="20" fill="currentColor" font-size="16">Visible bar · region · 3 s lead · build 4548</text>']
for t in (-45,0,33,75,125):svg.append(f'<line x1="{x(t)}" x2="{x(t)}" y1="45" y2="172" stroke="currentColor" opacity=".18"/><text x="{x(t)}" y="194" text-anchor="middle" fill="currentColor" font-size="12">{t:+} ms</text>')
for mode,y,color in [('on',80,'var(--chart-1)'),('off',140,'var(--chart-2)')]:
 svg.append(f'<text x="10" y="{y+5}" fill="currentColor" font-size="14">{mode.title()}</text>')
 for i,r in enumerate(a for a in rows if a['highlights']==mode):
  yy=y+(i-1.5)*10
  svg.append(f'<circle cx="{x(r["medianMs"])}" cy="{yy}" r="5" fill="{color}"/><text x="{x(r["medianMs"])+9}" y="{yy+4}" fill="currentColor" font-size="11">{i+1}: {r["medianMs"]:+g}</text>')
svg.append('<text x="80" y="221" fill="currentColor" font-size="12">Audio minus picture; positive = sound later. Acceptance: −45…+125 ms.</text></svg>')
svg=''.join(svg);(E/'comparison.svg').write_text(svg)
html='<style>:root{color:var(--foreground);font-family:var(--font-sans)}figure{margin:0;padding:16px;background:var(--card);border-radius:var(--radius)}svg{width:100%;height:auto;display:block}</style><figure>'+svg+'</figure>'
pathlib.Path('/tmp/b1364-visible/chart.html').write_text(html)
