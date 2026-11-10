import sys, unittest
from pathlib import Path
sys.path.insert(0, 'tests/ci')
import test_ubuntu_mirrors as t
t.WORKFLOWS = (Path('.github/workflows/ci.nightly.yml'),)
names = ['test_http_200_trickle_is_demoted_below_fast_mirror', 'test_dead_mirror_stays_last', 'test_all_slow_still_yields_usable_speed_ordered_list']
r = unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite(t.UbuntuMirrors(n) for n in names))
sys.exit(not r.wasSuccessful())
