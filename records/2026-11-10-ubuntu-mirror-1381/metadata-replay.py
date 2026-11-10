import sys, unittest
from pathlib import Path
sys.path.insert(0, 'tests/ci')
import test_ubuntu_mirrors as t
t.WORKFLOWS = (Path('.github/workflows/ci.metadata.yml'),)
names = ['test_http_200_trickle_is_demoted_below_fast_mirror']
r = unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite(t.UbuntuMirrors(n) for n in names))
sys.exit(not r.wasSuccessful())
