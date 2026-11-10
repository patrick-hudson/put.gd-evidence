import ast,pathlib,json
root=pathlib.Path.home()/'work/h1364/calibration';tree=ast.parse((root/'measure_rings.py').read_text());safe=[n for n in tree.body if isinstance(n,(ast.Import,ast.ImportFrom,ast.FunctionDef))];ns={};exec(compile(ast.Module(body=safe,type_ignores=[]),'ring functions','exec'),ns)
for name,wanted in [('monitor-on',True),('monitor-off',False)]:
 frames=ns['decoded'](root/'runs'/name/'out/pr-mp4-1.mp4',200,100,32);hits=[dict(ns['shape'](b),ms=t) for t,b in frames if ns['shape'](b)['seen']]
 assert bool(hits)==wanted,(name,hits[:1]);print(name,'ring',bool(hits),'first',hits[:1])
