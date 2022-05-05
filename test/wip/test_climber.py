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
   print('LPV ', listofpackversions)
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
        res = [True, 0, -1, -1]
    else:
        res = [False, pkg2int[status[1]], pkg2int[status[0]]]
        res = [False, 0, pkg2int[status[1]], pkg2int[status[0]]]

    return res

liquidparser.works = works2

###############################################################################


liquid.env.init(dir='/Users/pradal/devlp/project/vflexql/test/simple',
                universe=('foo', 'goo', 'hoo'))

liquid.activate()

ordered_packages = ('foo', 'goo', 'hoo')
sourcemap, default, todolist = liquid.variables_for_parser(ordered_packages)

_orderofpackages = ['hoo', 'goo', 'foo', 'hoo']
orderofpackages = [liquid.env.pkg2int[p] for p in _orderofpackages]

compatibilities = []

#results, compatibilities = liquid.experiment()

# set global variables
liquidparser.compatibilities = compatibilities
liquidparser.orderofpackages = orderofpackages
liquidparser.default = default
liquidparser.sourcemap = sourcemap
liquidparser.todolist = todolist
liquidparser.strongmemory = []

constraints = {}

try:
    endconfig = liquidparser.liquidclimber(constraints, todolist)
finally:
    liquid.restore_config()

# print results

#compatibilities= []
# compatibilities.append([1, 11, 11, 2, 21, 21])
# compatibilities.append([1, 12, 12, 2, 22, 22])
# compatibilities.append([1, 15, 15, 2, 28, 28])
# compatibilities.append([1, 11, 11, 3, 31, 31])
# compatibilities.append([1, 12, 12, 3, 32, 32])
# compatibilities.append([1, 15, 15, 3, 38, 38])
# compatibilities.append([1, 11, 11, 4, 41, 41])
# compatibilities.append([1, 12, 12, 4, 42, 42])
# compatibilities.append([1, 15, 15, 4, 48, 48])
# compatibilities.append([2, 21, 21, 3, 31, 31])
# compatibilities.append([2, 22, 22, 3, 32, 32])
# compatibilities.append([2, 28, 28, 3, 38, 38])
# compatibilities.append([2, 21, 21, 4, 41, 41])
# compatibilities.append([2, 22, 22, 4, 42, 42])
# compatibilities.append([2, 28, 28, 4, 48, 48])
# compatibilities.append([3, 31, 31, 4, 41, 41])
# compatibilities.append([3, 32, 32, 4, 42, 42])
# compatibilities.append([3, 38, 38, 4, 48, 48])

""" 
OLD BACKUP

orderofpackages = [1, 3, 4, 2, 3, 4, 3, 1, 2]

sourcemap = { 1: [11, 12, 13, 14, 15, 16, 17, 18, 19],
2: [21, 22, 23, 24, 25, 26, 27, 28, 29],
3: [31, 32, 33, 34, 35, 36, 37, 38, 39],
4: [41, 42, 43, 44, 45, 46, 47, 48, 49]}

default = {1:11,2:21, 3:31, 4:41} # configuration that works

constraints = {}
todolist = [3, 2, 4, 1]

# set global variables
liquidparser.compatibilities = compatibilities
liquidparser.orderofpackages = orderofpackages
liquidparser.default = default
liquidparser.sourcemap = sourcemap

endconfig = liquidparser.liquidclimber(constraints, todolist)
"""
