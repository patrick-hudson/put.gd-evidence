from tools.lab import lab
from pathlib import Path
r=Path('work/lab-runs/o1')
def typed(s):
 codes={'/':'slash','=':'equal','+':'equal',':':'semicolon',';':'semicolon','.':'dot','-':'minus','_':'minus'}
 for c in s:
  code=c.lower() if c.isalpha() else codes.get(c,c)
  keys=(['shift'] if c.isupper() or c in '+:_' else [])+[code]
  lab.key(r,keys)
if __name__=='__main__': typed('AZaz09+/=')
