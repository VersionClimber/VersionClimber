from VersionClimber_test1 import vclimb as vclimb1
from VersionClimber_test2 import vclimb as vclimb2

assert vclimb1.main() == 'a'
assert vclimb1.main() == vclimb2.main()
