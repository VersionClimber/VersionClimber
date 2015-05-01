"""
Climber test

1. Use liquidclimber on the simple test
  - map commit version and package name to integer 
  compute sourcemap
2. Remove the global variables

"""

from vflexql import liquid, liquidparser


###############################################################################

# MONKEY PATCHING

count = 0

def works(listofpackversions):
   print 'LPV ', listofpackversions
   history = []
   for p in liquidparser.orderofpackages:
    x = liquidparser.decidepackage(history, [p,listofpackversions[p]])
    if x[0]:
        history.append([p,listofpackversions[p]])
    else:
        return [False, p, x[1]]
   return [True, -1, -1] # -1 indicates all ok only use the True part


def works2(listofpackversions):
    global count
    count += 1

    config = listofpackversions
    int2pkg = liquid.env.int2pkg
    pkg2int = liquid.env.pkg2int

    bidir = liquid.env.bidir_commits
    semantic_config = {}
    for pi, ci in config.iteritems():
        pkg = int2pkg[pi]
        commit = bidir[pkg][1][ci]
        semantic_config[pkg] = commit

    for pkg, commit in semantic_config.iteritems():
        liquid.checkout(pkg, commit)
        liquid.pip_install(pkg)

    status = liquid.run()

    if status == 0:
        res = [True, -1, -1]
    else:
        res = [False, pkg2int[status[1]], pkg2int[status[0]]]

    return res

liquidparser.works = works2

###############################################################################


liquid.env.init(dir='/Users/pradal/devlp/project/vflexql/test/pkgs',
                universe=('scikit-image', 'scikit-learn'))

liquid.activate()

ordered_packages = ('scikit-image', 'scikit-learn')
default = dict(zip(ordered_packages, ['v0.4', '0.8']))
sourcemap, default, todolist = liquid.variables_for_parser(ordered_packages, default=default)


_orderofpackages = ['scikit-image', 'scikit-learn']
orderofpackages = [liquid.env.pkg2int[p] for p in _orderofpackages]

compatibilities = []

#results, compatibilities = liquid.experiment()

# set global variables
liquidparser.compatibilities = compatibilities
liquidparser.orderofpackages = orderofpackages
liquidparser.default = default
liquidparser.sourcemap = sourcemap

constraints = {}

try:
    endconfig = liquidparser.liquidclimber(constraints, todolist)
finally:
    liquid.restore_config()


"""
Initial config:

scikit-image : v0.4
scikit-learn : 0.8-branching

import git
from vflexql import liquid, liquidparser

liquid.env.init(dir='/Users/pradal/devlp/project/vflexql/test/pkgs',
                universe=('scikit-image', 'scikit-learn'), Tags=True)

commits = liquid.env.commits

liquid.env.commits = {p:[x for x in l if 'debian' not in str(x)] for p, l in commits.iteritems()}

p='pkgs/venv/bin/activate_this.py'
execfile(p, dict(__file__=p))

ordered_packages = ('scikit-image', 'scikit-learn')
default = dict(zip(ordered_packages, ['v0.4', '0.8']))
sourcemap, default, todolist = liquid.variables_for_parser(ordered_packages, default=default)

_orderofpackages = ['scikit-image', 'scikit-learn']
orderofpackages = [liquid.env.pkg2int[p] for p in _orderofpackages]

compatibilities = []

liquidparser.compatibilities = compatibilities
liquidparser.orderofpackages = orderofpackages
liquidparser.default = default
liquidparser.sourcemap = sourcemap

constraints = {}

endconfig = liquidparser.liquidclimber(constraints, todolist)

restore_config()



si_repo = git.Repo('pkgs/scikit-image/')
initial_si = si_repo.tags['v0.4'].commit

sl_repo = git.Repo('pkgs/scikit-learn/')
initial_sl = sl_repo.tags['0.8-branching'].commit

sl = liquid.env.commits['scikit-learn']
si = liquid.env.commits['scikit-image']

sl.index(initial_sl)
si.index(initial_si)


"""