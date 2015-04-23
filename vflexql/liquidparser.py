# This code is nearly ready for integration with Christophe.
# It must fill the variable sourcemap based on versions of each relevant
# package

# Eventually, we have to get a configuration file that holds (i) the constraints
# (ii) the packages that we want to maximize in descending order of priority
# (iii) the default configuration.
# For now, please look at constraints = ... and  todolist = 
# and default =

# To run this file simply run it without any further arguments, i.e.
# python liquidparser.py
# If you want to see how it works, then change the simulator by
# changing the parts labeled DATA



# The program:
# 
# Simulator of acceptable versions.
# (package1, versionlow1, versionhigh1, package2, versionlow2, versionhigh2)
# Semantics are that any version 
# between versionlow1 and versionhigh1
# of package 1 will work with any version 
# between versionlow2 and versionhigh2 of package 2.
# 
# Some random ordering of package/version pairs in an execution.
# 
# If the next package/version is incompatible with the 
# package/versions already seen then we have a failure with 
# an announcement of where bad.



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


#####################################
# global varable
#####################################

memory = {} # we will remember here the versions of package
    # combinations that don't work, so we don't redo them
    # we just keep exploring higher versions

axiom = {} # we use the historicity and failure monotonicity axioms
 # each element is keyed by two packages and has the format
 # (pack1, version1, lesseq/eq/greatereq, pack2, version2, lesseq/eq/greatereq)

#################################################################################
# Simulator code


# is ver1 of pack1 compatible with ver2 of pack2
# If the packages are the same then return true
# Could be compatible if there is no mention of the two versions
# or if there is a match
def compatible(packver1, packver2):
  pack1 = packver1[0]
  ver1 = packver1[1]
  pack2 = packver2[0]
  ver2 = packver2[1]
  bydefault = True
  if pack1 == pack2:
	return True
  for c in compatibilities:
    if (c[0] == pack1) and (c[3] == pack2): 
	bydefault = False # the two packages are in the list of compatibilities
    	if (ver1 >= c[1]) and (ver1 <= c[2]) and (ver2 >= c[4]) and (ver2 <= c[5]):
		return True
    if (c[0] == pack2) and (c[3] == pack1): 
	bydefault = False # the two packages are in the list of compatibilities
    	if (ver1 >= c[4]) and (ver1 <= c[5]) and (ver2 >= c[1]) and (ver2 <= c[2]):
		return True
  return bydefault # if we've never encountered these packages, we'll return
	# true, but if we have found the packages but no compatible versions,
	# then we'll return False
		

# Given a new package-version pair newpackver,
# is it compatible with the ones that are already there?
def decidepackage(historyofpackversions, newpackver):
   if 0 == len(historyofpackversions):
	return [True, newpackver[0]]
   h = historyofpackversions[-1] # only worry about the very last one
   if compatible(h, newpackver) == False:
	print "call on compatible ", h, " with ", newpackver, " has return value False."
	return [False, h[0]]
   else:
	print "call on compatible ", h, " with ", newpackver, " has return value True."
   	return [True, newpackver[0]]

# Does an execution work? If so return an empty list. 
# If not, return the package that failed.
def works(listofpackversions):
   history = []
   for p in orderofpackages:
	x = decidepackage(history, [p,listofpackversions[p]])
	if x[0]:
		history.append([p,listofpackversions[p]])
	else:
		return [False, p, x[1]]
   return [True, -1, -1] # -1 indicates all ok only use the True part


# APPLICATION-SPECIFIC (outside of simulator)

# filter the source based on constraints and output the result
def filtermap(sourcemap, constraints):
	out = {}
	for s in sourcemap.viewkeys():
		vals = sourcemap[s]
		if s in constraints.viewkeys():
			vals = [v for v in vals if (v >= constraints[s][0]) and (v <= constraints[s][1])]
		out[s] = copy.deepcopy(vals)
	return out


# flatten takes a list and creates a string with underbars
def flatten(list):
  out = ""
  for x in list:
	out+= (str(x))
	out+= '_'
  return out

# testaxiom looks at the various axioms to see
# whether a given call on newpackver from the last element of history
# has already been determined to be incompatible
# returns True if incompatibility else False if no trouble found
# element of axiomlist has format 
# (pack1, version1, lesseq/eq/greatereq, pack2, version2, lesseq/eq/greatereq)
def testaxiom(axiomlist, h, new):
    for a in axiomlist:
	if (h[0] == a[0]) and (new[0] == a[3]):
		hver = a[1]
		horientation = a[2]
		newpackver = a[4]
		newpackorientation = a[5]
	elif (h[0] == a[3]) and (new[0] == a[0]):
		hver = a[4]
		horientation = a[5]
		newpackver = a[1]
		newpackorientation = a[2]
	hsat = ((h[1] == hver) and (horientation == 'eq'))
	hsat = hsat or ((h[1] <= hver) and (horientation == 'lesseq'))
	hsat = hsat or ((h[1] >= hver) and (horientation == 'greatereq'))
	newpacksat  = ((new[1] == newpackver) and (newpackorientation == 'eq'))
	newpacksat  = newpacksat or ((new[1] <= newpackver) and (newpackorientation == 'lesseq'))
	newpacksat  = newpacksat or ((new[1] >= newpackver) and (newpackorientation == 'greatereq'))
	if hsat and newpacksat:
		return True
    return False


# Given a new package-version pair newpackver,
# is it compatible with the ones that are already there?
# Here we don't execute, but rather use memory
# and the axiom datastructures
def memorydecidepackage(historyofpackversions, newpackver):
   if 0 == len(historyofpackversions):
	return [True, newpackver[0]]
   for h in historyofpackversions:
	if flatten(h) in memory.viewkeys():
	   if newpackver in memory[flatten(h)]:
		print "memory call for  ", h, " with ", newpackver, " has return value False."
		return [False, h[0]]
   h = historyofpackversions[-1]
   x = flatten([h[0], newpackver[0]])
   if x in axiom.viewkeys():
	if testaxiom(axiom[x], h, newpackver):
		print "axiom call for  ", h, " with ", newpackver, " has return value False because of ", axiom[x]
		return [False, h[0]]
   return [True, newpackver[0]]

# First see whether we can determine that this won't work because
# of what we remember. If we can, then return False, 
# identify the offending package
# combinations and return a False indicating we did not need to to a real
# execution.
# Otherwise, do a real execution.
# If it succeeds, then return True, and three fields we don't care about.
# Otherwise, return False, identify the offending package combinations
# and return a True indicating we DID a real execution.
def checkworks(listofpackversions):
   history = []
   for p in listofpackversions:
	x = memorydecidepackage(history, [p,listofpackversions[p]])
	if x[0]:
		history.append([p,listofpackversions[p]])
	else:
		print "Have avoided an execution."
		return [False, p, x[1], False]
   # using memory did not exclude the possibility that this would work
   x = works(listofpackversions)
   print "Tested configuration: ", listofpackversions
   return [x[0], x[1], x[2], True]
	

# whichever version of badpack is in temp is incompatible with
# the version of badother in temp
# We are storing package version pairs and indexing by package version pairs.
# We also know which packages have been maximize pushed
def addtomemory(temp, badpack, badother, maxpushlist):
   verpack = temp[badpack]
   verother = temp[badother]
   x = flatten([badpack, verpack])
   if x not in memory.viewkeys():
	memory[x] = []
   memory[x].append([badother, verother])
   # x = flatten([badother, verother])
   # if x not in memory.viewkeys():
	# memory[x] = []
   # memory[x].append([badpack, verpack])
   x = flatten([badpack, badother])
   if x not in axiom.viewkeys():
	axiom[x] = []
   # if badother == maxpushlist[-1]:
   	# axiom[x].append([badpack, verpack, 'lesseq', badother, verother, 'eq'])
   if (not badother in  maxpushlist) and (not badpack in maxpushlist):
   	axiom[x].append([badpack, verpack, 'greatereq', badother, verother, 'lesseq'])

# by advancing versions as needed, try to make a compatible set of
# package-version pairs
# Side effect to memory in order to avoid unnecessary executions
# temp is the configuration of package-versions we are trying
# searchedpackage is the package that was pushed
def trytomakework(searchedpackage, temp, newsourcemap):
  x = checkworks(temp) # we simulate this now, but in general
	# this involves the creation of a frozen virtual machine
  print "Within trytomakework, works on ", temp, " has a return value of: ", x
  maximizepushlist = [searchedpackage]
  while x[0] == False:
     badpack = x[1]
     badother = x[2]
     if (x[3]): # x[3] is true if we really did execute
     	addtomemory(temp, badpack, badother, maximizepushlist)
     if badpack in maximizepushlist:
  	maximizepushlist.append(badother) # now will push that one
	badpack = badother
     print "Bad package is ", badpack
     if (temp[badpack] < max(newsourcemap[badpack])):
	  nexthope =min([v for v in newsourcemap[badpack] if v > temp[badpack]])
	  temp[badpack] = nexthope
  	  x = checkworks(temp) 
  	  print "Within while, works on ", temp, " has a return value of: ", x
     elif (temp[badother] < max(newsourcemap[badother])):
	  nexthope =min([v for v in newsourcemap[badother] if v > temp[badother]])
	  temp[badother] = nexthope
  	  x = checkworks(temp) 
  	  print "Within while, works on ", temp, " has a return value of: ", x
     else:
	  return {}
  return temp
  
	

# This implements the algorithm against our simulator, but eventually
# against a real system
# todolist gives the order of packages that must be maximized
def liquidclimber(constraints, todolist):
  newsourcemap = filtermap(sourcemap, constraints)
  print "newsourcemap is: ", newsourcemap
  current = copy.deepcopy(default)
  for m in todolist: # todolist gives the packages to maximize
	# in descending order of priority
	maxmyversions = max(newsourcemap[m])
	print "package to optimize is: ", m
	print "current is: ", current
	if (current[m] < maxmyversions):
		versionstodo = sorted([v for v in newsourcemap[m] if v > current[m]])
		print "versionstodo is: ",versionstodo
		# versions still to try
		for v in versionstodo:
		   # if keepwork:
			# print "v is: ", v
			temp = copy.deepcopy(current)
			temp[m] = v
			ret = trytomakework(m, temp, newsourcemap)
			# print "return value: ", ret, " for config: ", temp
			if 0 < len(ret):
				current = copy.deepcopy(ret)
			# else:
				# keepwork = False # higher versions also bad 
  return current

	
	
	
'''
# DATA

# For simulator
	
	

# compatibilities= []
# compatibilities.append([1, 11, 13, 2, 21, 23])
# compatibilities.append([1, 11, 13, 3, 31, 33])
# compatibilities.append([1, 11, 13, 4, 41, 43])
# compatibilities.append([1, 16, 19, 2, 27, 29])
# compatibilities.append([1, 16, 19, 3, 37, 39])
# compatibilities.append([1, 16, 19, 4, 47, 49])
# compatibilities.append([2,21,24, 3, 31, 34])
# compatibilities.append([2,27,29, 3, 36, 39])
# compatibilities.append([2,21,24, 4, 41, 44])
# compatibilities.append([2,27,29, 4, 46, 49])
# compatibilities.append([3,31,34, 4, 41, 45])
# compatibilities.append([3,36,37, 4, 46, 49])

compatibilities= []
compatibilities.append([1, 11, 13, 2, 21, 24])
compatibilities.append([1, 18, 19, 2, 28, 29])
compatibilities.append([1, 11, 13, 3, 31, 34])
compatibilities.append([1, 18, 19, 3, 38, 39])
compatibilities.append([1, 11, 13, 4, 41, 44])
compatibilities.append([1, 18, 19, 4, 48, 49])
compatibilities.append([2,21,29, 3, 31, 39])
compatibilities.append([2,21,24, 4, 41, 44])
compatibilities.append([2,28,29, 4, 48, 49])
compatibilities.append([3,31,34, 4, 41, 45])
compatibilities.append([3,38,39, 4, 48, 49])


compatibilities= []
compatibilities.append([1, 11, 11, 2, 21, 21])
compatibilities.append([1, 12, 12, 2, 22, 22])
compatibilities.append([1, 15, 15, 2, 24, 24])
compatibilities.append([1, 11, 11, 3, 31, 31])
compatibilities.append([1, 12, 12, 3, 32, 32])
compatibilities.append([1, 15, 15, 3, 34, 34])
compatibilities.append([1, 11, 11, 4, 41, 41])
compatibilities.append([1, 12, 12, 4, 42, 42])
compatibilities.append([1, 15, 15, 4, 44, 44])
compatibilities.append([2, 21, 21, 3, 31, 31])
compatibilities.append([2, 22, 22, 3, 32, 32])
compatibilities.append([2, 24, 24, 3, 34, 34])
compatibilities.append([2, 21, 21, 4, 41, 41])
compatibilities.append([2, 22, 22, 4, 42, 42])
compatibilities.append([2, 24, 24, 4, 44, 44])
compatibilities.append([3, 31, 31, 4, 41, 41])
compatibilities.append([3, 32, 32, 4, 42, 42])
compatibilities.append([3, 34, 34, 4, 44, 44])

compatibilities= []
compatibilities.append([1, 11, 13, 2, 21, 24])
compatibilities.append([1, 14, 17, 2, 25, 26])
compatibilities.append([1, 11, 13, 3, 31, 34])
compatibilities.append([1, 14, 17, 3, 35, 38])
compatibilities.append([1, 11, 13, 4, 41, 44])
compatibilities.append([1, 14, 17, 4, 45, 46])
compatibilities.append([2,21,29, 3, 31, 39])
compatibilities.append([2,21,24, 4, 41, 44])
compatibilities.append([2,26,28, 4, 45, 49])
compatibilities.append([3,31,34, 4, 41, 45])
compatibilities.append([3,36,37, 4, 46, 49])

compatibilities= []
compatibilities.append([1, 11, 13, 2, 21, 24])
compatibilities.append([1, 14, 17, 2, 25, 26])
compatibilities.append([1, 11, 13, 3, 31, 34])
compatibilities.append([1, 14, 17, 3, 35, 38])
compatibilities.append([1, 11, 13, 4, 41, 44])
compatibilities.append([1, 14, 17, 4, 45, 46])
compatibilities.append([2,21,29, 3, 31, 39])
compatibilities.append([2,21,24, 4, 41, 44])
compatibilities.append([2,26,28, 4, 45, 49])
compatibilities.append([3,31,34, 4, 41, 45])
compatibilities.append([3,36,37, 4, 46, 49])

compatibilities= []
compatibilities.append([1, 11, 11, 2, 21, 21])
compatibilities.append([1, 12, 12, 2, 22, 22])
compatibilities.append([1, 19, 19, 2, 28, 28])
compatibilities.append([1, 11, 11, 3, 31, 31])
compatibilities.append([1, 12, 12, 3, 32, 32])
compatibilities.append([1, 19, 19, 3, 38, 38])
compatibilities.append([1, 11, 11, 4, 41, 41])
compatibilities.append([1, 12, 12, 4, 42, 42])
compatibilities.append([1, 19, 19, 4, 48, 48])
compatibilities.append([2, 21, 21, 3, 31, 31])
compatibilities.append([2, 22, 22, 3, 32, 32])
compatibilities.append([2, 28, 28, 3, 38, 38])
compatibilities.append([2, 21, 21, 4, 41, 41])
compatibilities.append([2, 22, 22, 4, 42, 42])
compatibilities.append([2, 28, 28, 4, 48, 48])
compatibilities.append([3, 31, 31, 4, 41, 41])
compatibilities.append([3, 32, 32, 4, 42, 42])
compatibilities.append([3, 38, 38, 4, 48, 48])

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


# outside of the simulator


memory = {} # we will remember here the versions of package
	# combinations that don't work, so we don't redo them
	# we just keep exploring higher versions

axiom = {} # we use the historicity and failure monotonicity axioms
 # each element is keyed by two packages and has the format
 # (pack1, version1, lesseq/eq/greatereq, pack2, version2, lesseq/eq/greatereq)


sourcemap = { 1: [11, 12, 13, 14, 15, 16, 17, 18, 19],
2: [21, 22, 23, 24, 25, 26, 27, 28, 29],
3: [31, 32, 33, 34, 35, 36, 37, 38, 39],
4: [41, 42, 43, 44, 45, 46, 47, 48, 49]}

default = {1:11,2:21, 3:31, 4:41} # configuration that works

# constraints indicate low and high versions
# if no constraints, then take every one
# constraints = { 1: [12, 15], 2:[21,27]}
# map from package to low allowed version to high version inclusive
constraints = { 1: [11, 19], 2:[21,28]}
todolist = [3,1]

# EXECUTION

print "Start with this: ",default

endconfig = liquidclimber(constraints, todolist)
print "End with this: ",endconfig


'''
