
# parser for the access language for version flexible software
# Takes as input a cross-product of versions 
# in the form of a dictionary mapping source to a list of version numbers
# and an ordered set of constraints
# of the form
# [source, low interval value, high interval value]
# and outputs a prioritized list of version combinations to try.


import sys
import math
import csv
import os
import copy
import operator
import doctest
import itertools
import collections
import datetime
import random
from operator import itemgetter, attrgetter
sys.setrecursionlimit(20000) 

now = datetime.datetime.now()
currentyear = now.year

# APPLICATION-SPECIFIC

# flatten an array into a string
def flatten(arr):
     out=""
     for a in arr:
        out+=str(a)
     return out

def crossproduct(somelists):
	out = []
	for element in itertools.product(*somelists):
    		out.append(element)
	return out

def prioritizeorder(versions, defaults):
	out = crossproduct(versions)
	j = len(defaults) - 1
	newversions = copy.deepcopy(versions)
	while ( j > -1):
		if (newversions[j] != [defaults[j]] ):
			newversions[j] = [defaults[j]]
			yy = crossproduct(newversions)
			for y in yy:
				out.append(y)
		j -= 1
	return out

# construct the versions in order of the constraints
def constructversions(sourcemap, constraints, defaultmap):
	out = []
	mykeys = sourcemap.keys()
	outkeylist = []
	for c in constraints:
		allversions = sourcemap[c[0]] # all versions from this source
		filteredversions = []	
		for a in allversions:
			if (3 == len(c)):
			   if (a >= c[1]) and (a <= c[2]):
				filteredversions.append(a)
			if (2 == len(c)):
			   if (a == c[1]): 
				filteredversions.append(a)
		out.append(filteredversions) # will go into versions
		outkeylist.append(c[0])
		mykeys.remove(c[0])
	for mysource in mykeys:
		print 'mysource is: ', mysource
		outkeylist.append(mysource)
		out.append([defaultmap[mysource]])
	print 'have handled constraints; out is: ', out
	pair = [out, outkeylist]
	return pair

# construct the versions in the same order as the versions
def constructdefaults(defaultmap, sourcenames):
	out = []
	for s in sourcenames:	
		out.append(defaultmap[s])
	return out

# DATA

# sources and versions  will be retrieved from the liquid virtual machine
sourcemap = { 'source1' : [3.0, 4.0], 'source2' : [0.1, 0.2, 1.0, 1.1, 1.2, 1.3, 2.2], 'source3' : [1.1, 2.0, 2.5, 3.1, 3.2], 'source4' : [1.1, 1.2, 1.3]}

# sources and their defaults also
defaultmap = {'source4':  1.2, 'source1': -3.0, 'source2': -2.0, 'source3': -1.0, 'source4': -4.0}

# constraints will be the result of a parse of a query
# Any constraint not taken will use the default value
constraints = [ ['source2', 1.1, 1.3], ['source3', 1.9, 2.5], ['source1', 4.0]]

versions = [[1.1, 1.2, 1.3], [2.0, 2.5], [4.0]]
defaults = [-1.0, -2.0, -3.0]

# EXECUTION


pair = constructversions(sourcemap, constraints, defaultmap)
versions = pair[0]
sourcenames = pair[1]

defaults = constructdefaults(defaultmap, sourcenames)


out = prioritizeorder(versions, defaults)

print sourcenames
for rec in out:
    recstring=''
    for myfield in rec:
	recstring+= str(round(myfield,3))
	recstring+= ", "
    print recstring[:-2]
