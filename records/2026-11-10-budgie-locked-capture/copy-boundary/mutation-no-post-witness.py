from pathlib import Path
p=Path('/home/patrick/work/pg-cd/src/platform/budgie/BudgieSourceAdapter.cpp');s=p.read_text();Path('/tmp/pg-r2-valid-adapter.cpp').write_text(s)
a=s.index('     guard->queryVisibility([guard,generation,complete,image=std::move(image)]')
b=s.index('     });',a)+len('     });')
s=s[:a]+'     complete(std::move(image),{});'+s[b:]
a=s.index('   guard->queryVisibility([guard,generation,frozen,revision,frames=std::move(frames)')
b=s.index('   });',a)+len('   });')
s=s[:a]+'   cb(std::move(frames),{});'+s[b:]
p.write_text(s)
