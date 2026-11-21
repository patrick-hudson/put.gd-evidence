# fastpace.py SESS.py: LAB_FAST=1 = recheck-2's faster pace (18-notch commands, 60 ms apart)
import sys
p = sys.argv[1]; s = open(p).read()
old = """        wheel('w %d' % rng.choice([1, 2, 3, 3, 4, 5]))
        time.sleep(rng.uniform(1.2, 2.2) if rng.random() < 0.06 else rng.uniform(0.15, 0.45))"""
assert s.count(old) == 1
new = """        if os.environ.get('LAB_FAST') == '1':
            # #1557: the faster pace of the re-check (Afast): 18-notch commands, 60 ms apart.
            wheel('w 18')
            time.sleep(0.06)
            continue
""" + old
s = s.replace(old, new); open(p, 'w').write(s); print('fast pace patched')
