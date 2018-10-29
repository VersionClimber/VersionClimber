# The master program gets the configurations as a text file, with one package
# per line in the format
# major.minor versions in ascending order.
# Packages are in their priority order from highest to lowest.
# The algorithm first sends to clients the maximum of each major release
# then if release x works but x+1 doesn't, test the ones in between.
# The implicit assumption is that if major release x+1 with the max
# of the minor version doesn't work, then no minor version of major release
# x+2 will work.
# This is not really justifiable I don't think but is good for quick and
# dirty. The manager also keeps track of already tried configurations,
# so nothing is tried again.
# The call to each client will be  of the form ['4.5', '3.9', '1.3']
# that is a configuration that checkworks will test
# The output will be the highest major configurations found and then the
# highest overall.

# For the sake of simulation the checkworks function
# will have a probability
# for each configuration to determine whether it is good or not.
# Of course, this will be a real test eventually.

# If a configuration has failed for one slave, no other slave
# gets that configuration.
# If a configuration succeeds for one or more slaves, the master
# keeps track of that information in configstats.

# configstat maps configurations to a vector that is as long as
# the number of slaves.
# For a particular configuration c, configstat[c] is set to all 0s.
# If slave i succeeds with configuration c, then the ith
# entry of configstat[c] is set to +1.
# If slave i fails with configuration c, then the ith
# entry of configstat[c] is set to -1.
# Configuration c succeeds if the min value is 1. It fails if the min value
# is -1.
#CPL
from __future__ import absolute_import
from __future__ import print_function

# Christophe
#import zmq, time, math
import zmq, time, math
import copy
import logging

#CPL
import itertools
#context = zmq.Context()
#socket = context.socket(zmq.REP)
#socket.bind("tcp://*:50008")

# Christophe
log_file = 'versionclimber.log'

def start_logging(log_file=log_file):
    logging.basicConfig(filename=log_file, level=logging.DEBUG)
    logging.info("Hello"+ 'world'+ str(5)+ str(4.1))

# End Christophe

# FUNCTIONS

# generate the cross-product of the anchor configurations in descending
# order in first phase
# In second phase try one supply-constant mini-series that is a candidate
# at a time with the other anchors.
def genconfigs(miniseries, packageversions, anchorFlag):
  if anchorFlag == True:
    myanchors = findanchors(miniseries)
    return mycrossproduct_iter(myanchors)
  else:
    # just go through all configurations
    return mycrossproduct_iter(packageversions)



# return the cross product in descending order
def mycrossproduct(packageversions):
  reversed = packageversions[::-1]
  currentcross = [[x] for x in reversed[0][::-1]]
  i = 1
  while (i < len(reversed)):
    row = reversed[i][::-1]
    out = []
    for r in row:
      for c in currentcross:
        out.append([r]+c)
    currentcross = copy.deepcopy(out)
    i+= 1
  return currentcross

def mycrossproduct_iter(packageversions):
  # return the different versions of each package using a reverse iterators
  iterators= map(reversed, packageversions)

  # return an iterator of the cross product of each packageversion iterator
  # by varying the latest one
  gen = itertools.product(*iterators)

  nb_versions = 1
  for pkgvers in packageversions:
    nb_versions *= len(pkgvers)

  return nb_versions, gen

# findanchors for each supply-constant mini-series, this will take the
# minimum minor version.
# For each demand-constant mini-series, it will take the last one.
# Thus, this function finds the anchors of each miniseries
def findanchors(miniseries):
  out = []
  i = 0
  currentpackage = ''
  new = []
  for p in miniseries:
    if not p[0] == currentpackage:
      currentpackage = p[0]
      if 0 < len(new):
        out.append(new)
        new = []
    if p[1] == 'demand-constant':
      new.append([p[0], p[2][-1]])
    elif p[1] == 'supply-constant':
      new.append([p[0], p[2][0]])
  if 0 < len(new):
    out.append(new)
  return out


# take only the latest minors of each major
def slim(packageversions):
  out = []
  for  p in packageversions:
    new = findhighestperpackage(p)
    out.append(new)
  return out

# find the highest minor for each major per package
def findhighestperpackage(line):
  out = [line[0]]
  i = 1
  currentmajornum = -1
  last = ''
  lasttakenflag = False
  while (i < len(line)):
    x = line[i]
    pv = x.split(".")
    if (0 < len(last)) and (pv[0] != currentmajornum):
      out.append(last)
      if i == ((len(line)) - 1):
        lasttakenflag = True
    currentmajornum = pv[0]
    last = x
    i+= 1
  if lasttakenflag == False:
    out.append(last)
  return out



# find work for this slave from 0. We always start from 0 because we'll find the
# right index.
# Pass by all configs that have a -1 (indicating failure).
# If they all have failed then there is nothing good
def requestwork(slaveid, configindex):
   configindex = 0 # ignore the index from the slave in fact
   i = configindex
   c = configs[i]
   string_c = '_'.join(c)
   if (configstat[string_c][slaveid] == 1): # this was good for us
     if min(configstat[string_c]) == 1:
       # print "Success with: ", configs[i]
       return(str(i) + ' ' + string_c + ' Success')
     if min(configstat[string_c]) == 0:
       # print "Slave ", slaveid, " has had success with configuration ", c, " and will wait "
       return(str(i) + ' ' + string_c + ' Already_done')
   i = configindex + 1
   if i < len(configs):
     c = (configs[i])
   while(i < len(configs)):
     c = (configs[i])
     string_c = '_'.join(c)
     if 0 == min(configstat[string_c]): # still unknown
       return(str(i) + ' ' + string_c + ' Not_yet')
     if 1 == min(configstat[string_c]): # still unknown
       return(str(i) + ' ' + string_c + ' Success')
     i+= 1
   return(str(i) + ' ' +  'Non-existentconfig'  + ' Tried_everything')

# if the slave succeeded at this config, then set the appropriate element
# of configstat vector to status (and check whether that is a good config).
# 1 will be a success status and -1 a failure status.
def updatestatus(slaveid, configindex, status):
  global configstat, majorconfig
  c = (configs[configindex])
  string_c = '_'.join(c)
  configstat[string_c][slaveid] = status
  if 1 == min(configstat[string_c]):
    if (0 == len(majorconfig)):
      majorconfig = c
    # print "configuration: ", c , " works."
    return (["Success", c])
  return (["Keep_going", c])

# assemble a configuration from cand at position j of bestanchor
def assembleconfig(cand, j, bestanchor):
  myconfig = []
  i = 0
  while i < len(bestanchor):
    if (i == j):
      myconfig.append(cand)
    else:
      myconfig.append(bestanchor[i])
    i+= 1
  return myconfig

#  Given a pv = bestanchor[j]
# which is a package-value of one of the anchors that
# came from the first phase, find a potentially better package-value
# from the mini-series containing pv if that mini-series is supply-constant
# or is pv  itself if that mini-series is demand-constant.
# This will return a new package-value which will replace pv in the anchors.
def findbetterpackval(bestanchor, j, miniseries):
  pv = bestanchor[j]
  for m in miniseries:
    if (m[0] == pv[0]) and (pv[1] in m[2]) and (m[1] == 'demand-constant'):
      return bestanchor[j] # already the best of the mini-series
    if (m[0] == pv[0]) and (pv[1] in m[2]) and (m[1] == 'supply-constant'):
      mymini = m[2]
      badindex = len(mymini) # impossibly high
      # first try the highest
      k = badindex - 1
      cand = [pv[0], mymini[k]]
      c = assembleconfig(cand, j, bestanchor)
      if works(c):
        goodindex = k
        return ([pv[0], mymini[goodindex]])
      else:
        badindex = k

      # Now do binary search normally
      goodindex = 0 # this is the anchor
      k = int(goodindex + math.ceil((badindex - goodindex)/2))
      while (k > goodindex) and (k < badindex):
        cand = [pv[0], mymini[k]]
        c = assembleconfig(cand, j, bestanchor)
        if works(c):
          goodindex = k
        else:
          badindex = k
        k = int(goodindex + math.ceil((badindex - goodindex)/2))
      return ([pv[0], mymini[goodindex]])
  return bestanchor[j]

# ===========

# Christophe: as usual, replace works by a real call

goodconfigs = []

# try a configuration
# The configuration is a string where version specs are separated by '_'
# Christophe should replace this by an actual attempt to execute this
# configuration.
def works(c):
   global totaltests
   # print "configuration ", c, " is to be tested."
   totaltests+= 1
   for e in c:
     if ('1.0.1' in e) and ('Python' in e): # Just for testing.
       return False
   return True

# This would normally call tryworks or something
def tryconfig(c):
  if c in goodconfigs:
    return 1
  if works(c):
    goodconfigs.append(c)
    return 1
  else:
    return -1

# ===========
# packageversions = []
# miniseries = [] # triples of package, supplyordemand, elements

def read_packageversions(fn):
  fileicareabout = open(fn,"r")
  pv = fileicareabout.read().splitlines()
  fileicareabout.close()
  packageversions = []
  miniseries = [] # triples of package, supplyordemand, elements
  lineispackage = True
  bufferofpackages = []
  currentpackage = ''
  for line in pv:
   if 0 == len(line): # end of package
     if 0 < len(bufferofpackages):
       packageversions.append(bufferofpackages)
       bufferofpackages = []
     lineispackage = True
   elif lineispackage == True:
     x = line.split(" ")
     currentpackage = x[0]
     lineispackage = False
   else: # we now have a miniseries
     y = line.split(" ")
     x = []
     for e in y:
      if 0 < len(e): x.append(e)
     for e in x[1:]:
       bufferofpackages.append([currentpackage, e])
     miniseries.append([currentpackage,x[0], x[1:]])
  if 0 < len(bufferofpackages):
    packageversions.append(bufferofpackages)
  return packageversions, miniseries

# Christophe : main program
def liquidclimber(miniseries, packageversions, anchorFlag=True):
  nb_configs, configs = genconfigs(miniseries, packageversions, anchorFlag)
  if anchorFlag == True:
    #print('Here are the anchors to try: ', configs)
    print('Number of anchors to try: ', nb_configs)
  if anchorFlag == False:
    print('Here is the number of configurations potentially to explore: ', nb_configs)
  notDone = True
  i = 0
  bestanchor = []
  while (i < nb_configs) and notDone:
    c = list(configs.next())
    i = i+1
    if tryconfig(c) == 1:
      notDone = False
      if anchorFlag == False:
        # We're done because anchorFlag == False means we do
        # a lexicographic sort of all possible configurations
        print("Here is the best final configuration using a complete lexicographic sort: ", c)
        return c
      elif anchorFlag == True:
        print("Here is the best anchor configuration: ", c)
        bestanchor = copy.deepcopy(c)
        j = 0
        while j < len(c):
          x = findbetterpackval(bestanchor, j, miniseries)
          bestanchor[j]  = copy.deepcopy(x)
          j+= 1
        print("Here is the best final configuration: ", bestanchor)

  # print("Total configurations tested is: ", totaltests)
  if not bestanchor:
    print("No configuration found that works")
  return bestanchor


if __name__ == '__main__':

  # EXECUTION

  # list of all connections

  # print 'miniseries are: ', miniseries
  # print 'packageversions are: ',  packageversions


  anchorFlag = True # if True use the mini-series anchor structure
    # If False, consider all configurations

  totaltests = 0

  packageversions, miniseries = read_packageversions("packageversions")

  print("PackageVersions", packageversions)
  print("miniseries", miniseries)

  #configs = genconfigs(miniseries, packageversions, anchorFlag)

  bestanchor = liquidclimber(miniseries, packageversions, anchorFlag)
