"""
Climber test
"""

from vflexql import liquid, liquidparser

liquid.init(dir='/Users/pradal/devlp/project/vflexql/test/simple',
     universe=('foo', 'goo', 'hoo'))

liquid.activate()

#results = liquid.experiment()
#print results

compatibilities= []
compatibilities.append([1, 11, 11, 2, 21, 21])
compatibilities.append([1, 12, 12, 2, 22, 22])
compatibilities.append([1, 15, 15, 2, 28, 28])
compatibilities.append([1, 11, 11, 3, 31, 31])
compatibilities.append([1, 12, 12, 3, 32, 32])
compatibilities.append([1, 15, 15, 3, 38, 38])
compatibilities.append([1, 11, 11, 4, 41, 41])
compatibilities.append([1, 12, 12, 4, 42, 42])
compatibilities.append([1, 15, 15, 4, 48, 48])
compatibilities.append([2, 21, 21, 3, 31, 31])
compatibilities.append([2, 22, 22, 3, 32, 32])
compatibilities.append([2, 28, 28, 3, 38, 38])
compatibilities.append([2, 21, 21, 4, 41, 41])
compatibilities.append([2, 22, 22, 4, 42, 42])
compatibilities.append([2, 28, 28, 4, 48, 48])
compatibilities.append([3, 31, 31, 4, 41, 41])
compatibilities.append([3, 32, 32, 4, 42, 42])
compatibilities.append([3, 38, 38, 4, 48, 48])

orderofpackages = [1, 3, 4, 2, 3, 4, 3, 1, 2]

sourcemap = { 1: [11, 12, 13, 14, 15, 16, 17, 18, 19],
2: [21, 22, 23, 24, 25, 26, 27, 28, 29],
3: [31, 32, 33, 34, 35, 36, 37, 38, 39],
4: [41, 42, 43, 44, 45, 46, 47, 48, 49]}

default = {1:11,2:21, 3:31, 4:41} # configuration that works

constraints = {}
todolist = [3,1]

# set global variables
liquidparser.compatibilities = compatibilities
liquidparser.orderofpackages = orderofpackages
liquidparser.default = default
liquidparser.sourcemap = sourcemap

endconfig = liquidparser.liquidclimber(constraints, todolist)

"""
d = liquid.env.commits
commits2int = {}
for k, v in d.iteritems():
    commits2int[k] = dict(enumerate(reversed(v)))
print commits2int
"""
