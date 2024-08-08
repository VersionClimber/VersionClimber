
# Assume we have input rows each of whose fields has the format package__version
# So we might have P1__3 P2__5 P3__6
# Another row might be P2__3 P4__7
# Each row represents a constraint.
# Each set of rows represents constraints between the same sets of packages.
# Different sets of rows are separated by a blank line.

# Here is a possible set of rows (in file "foobar")
"""
[P1__3 P1__4] [P2__3 P2__4 P2__5] P3_6
P1__4 P2__4 P3__19

P2__4 P4__7
P2__4 P4__8
P2__4 P4__9

P1__4 P6__1
P1__4 P6__2
"""

# The brackets indicate possible versions of packages.
# So the first row expands out to:
"""
P1__3 P2__5 P3__6
P1__3 P2__4 P3__6
P1__3 P2__3 P3__6
P1__4 P2__5 P3__6
P1__4 P2__4 P3__6
P1__4 P2__3 P3__6
"""

# The first group is the union of the results of each line in
# the groups (i.e. before an emptye line or the end).
# The first group expands to:
"""
P1__3 P2__5 P3__6
P1__3 P2__4 P3__6
P1__3 P2__3 P3__6
P1__4 P2__5 P3__6
P1__4 P2__4 P3__6
P1__4 P2__3 P3__6
P1__4 P2__4 P3__19
"""

# The second group yields:
"""
P2__4 P4__7
P2__4 P4__8
P2__4 P4__9
"""

# The outer join of the first group and the second group is the same as
# taking a cross product of pairs and then keep only those
# rows where the version numbers for the same package are the same.
# This is done by crossprodsel
# So if we take a cross-product between the first group and the second
# group and do the selection, we get
"""
P1__3 P2__4 P3_6 P4__7
P1__3 P2__4 P3_6 P4__8
P1__3 P2__4 P3_6 P4__9
P1__4 P2__4 P3_6 P4__7
P1__4 P2__4 P3_6 P4__8
P1__4 P2__4 P3_6 P4__9
P1__4 P2__4 P3__19 P4__7
P1__4 P2__4 P3__19 P4__8
P1__4 P2__4 P3__19 P4__9
"""
# The last group 
# constrains P1 and P6: 
# P1__4 [P6__1 P6__2]
# P1__9 P6__3
# An outerjoin with that group yields
"""
P1__4 P2__4 P3_6 P4__7 P6__1
P1__4 P2__4 P3_6 P4__7 P6__2
P1__4 P2__4 P3_6 P4__8 P6__1
P1__4 P2__4 P3_6 P4__8 P6__2
P1__4 P2__4 P3_6 P4__9 P6__1
P1__4 P2__4 P3_6 P4__9 P6__2
P1__4 P2__4 P3__19 P4__7 P6__1
P1__4 P2__4 P3__19 P4__7 P6__2
P1__4 P2__4 P3__19 P4__8 P6__1
P1__4 P2__4 P3__19 P4__8 P6__2
P1__4 P2__4 P3__19 P4__9 P6__1
P1__4 P2__4 P3__19 P4__9 P6__2
"""

# So we're taking the union of the constraints within each group
# and taking the outer join between groups

import copy

# This is an outerjoin: on any common packages they must
# agree but on the symmetric difference of packages they are just 
# added in. 
# Each group should have the same schema (i.e. the same set of packages)
# So for each row in the cross product of rows having package sets P1 and P2, 
# the number of unique package-version values 
# should be equal to the cardinality of P1 union P2
def crossprodsel(arr1, arr2):
  if testlevel > 0:
    print("arr1 is: ")
    [print(x) for x in arr1]
    print("arr2 is: ")
    [print(x) for x in arr2]
  res = [sub1 + " " + sub2 for sub1 in arr1 for sub2 in arr2]
  out = []
  # for an element of the cross-product to survive after taking the 
  # First find out how many unique packages in the union.
  if (len(res)) > 0:
    if testlevel > 0:
      print("res: ")
      print(res)
    firstline = (res[0]).split(" ")
    if testlevel > 0:
      print("firstline: ")
      print(firstline)
    p = findpackage(firstline)
    desiredlength = len(p)
  for r in res:
    sfields = r.split(" ")
    fields = [*set(sfields)] # remove duplicates
    if (len(fields) == desiredlength): # no mismatches
     fields.sort() 
     out.append(' '.join(fields))
  return out



# This function takes a row which might have brackets and performs an expansion.
# For example, it could take:
"""
[P1__3 P1__4] [P2__3 P2__4 P2__5] P3_6
"""
# and expand it to:
"""
P1__3 P2__5 P3__6
P1__3 P2__4 P3__6
P1__3 P2__3 P3__6
P1__4 P2__5 P3__6
P1__4 P2__4 P3__6
P1__4 P2__3 P3__6
"""
def expandrow(r):
  pair = parserow(r)
  simples = copy.deepcopy(pair[0])
  groups = copy.deepcopy(pair[1])
  if len(groups) == 0:
    return(r)
  out = groups[0]
  i = 1
  while i < len(groups):
    out = [sub1 + " " + sub2 for sub1 in out for sub2 in groups[i]]
    i+=1
  if len(simples) == 0:
    return out
  else:
    return [sub1 + " " + sub2 for sub1 in simples for sub2 in out]
  
    

# This function takes a row which might have brackets and separates groups
# from simples.
# For example, it could take:
"""
[P1__3 P1__4] [P2__3 P2__4 P2__5] P3_6
"""
# and return the pair
# [simples, vgroups]
# where simples would be 
"""
[P3_6]
"""
# and vgroups would be 
"""
[[P1__3, P1__4], [P2__3, P2__4, P2__5]]
"""
def parserow(r):
  vgroups =[]
  simples = []
  groupmode = 0
  chunks = r.split(" ")
  currentgroup = []
  for c in chunks:
    myc = c.strip()
    if (groupmode == 1) and (len(myc) > 0):
      if "]" == myc[-1]: # last character is "]"
        if len(myc) > 2: # there is a package
          currentgroup.append(myc.strip("]")) 
          vgroups.append(currentgroup)
          groupmode = 0
        else: # no package-version pair but still "]"
          vgroups.append(currentgroup)
          groupmode = 0
      else: # no "]" but in group mode
        currentgroup.append(myc) 
    elif (groupmode == 0) and (len(myc) > 0):
      if "[" == myc[0]: # first character is "["
        groupmode = 1
        currentgroup = []
        if len(myc) > 2: # there is a package
          currentgroup.append(myc[1:])
      elif len(myc) > 2: # just a simple package-version
        simples.append(myc)
  return [simples, vgroups] 

# finds the packages in the format [P1__xyz, P2__jkjk, P3__jkjj]
# Comes up with P1, P2, P3 in this case
def findpackage(mylist):
  j = 0
  packages = []
  while j < len(mylist):
    f = mylist[j]
    packages.append((f.split("__"))[0])
    j+= 1
  s = set(packages)
  if (testlevel > 0):
    print("set of packages: ")
    print(s)
  return s

# finds newgroups that have common packages  with at least one other newgroup
def findconnected(newpackages):
  out = []
  i = 0 
  while i < len(newpackages):
    if i not in out:
      j = i+1
      while j < len(newpackages):
        if not newpackages[i].isdisjoint(newpackages[j]):
          out.append(i)
          out.append(j)
        j+=1
    i+=1
  return list(set(out))
    
# finds the best join order among newgroups based on package
# intersection and size
def findnewgrouporder(newpackages, newsizes):
  firstcands = findconnected(newpackages) # candidates for first group
       # must be joinable to at least one other group
  minindex = newsizes.index(min(newsizes))
  if not minindex in firstcands:
    minindex = firstcands[-1] # That will probably be the smallest set
  ind = [minindex] # start with newgroup minindex
  packagessofar = newpackages[minindex]
  flag = True # have more work to do
  while(flag):
    flag = False
    i = 0
    cands = []
    mincandsize = 1 + max(newsizes)
    while(i < len(newpackages)):
      if (not i in ind) and (not packagessofar.isdisjoint(newpackages[i])):
        cands.append(i)
        if newsizes[i] < mincandsize: 
          mincandsize = newsizes[i]
      i+= 1
    if len(cands) > 0: 
      flag = True
      for j in cands:
        if (newsizes[j] == mincandsize):
          ind.append(j)
          packagessofar=packagessofar.union(newpackages[j])
  if len(ind) < len(newpackages):
    i = 0
    while(i < len(newpackages)):
      if not i in ind:
        ind.append(i)
      i+= 1
  print("ind is:")
  print(ind)
  return(ind)
   
    
    
    
  


# DATA

def reduce_config(text: list):
  #myfile=open(filename,"r")


  # EXECUTION

  # One line of constraints at a time
  #text=myfile.readlines()
  groups =[] # these will be groups of constraints pertaining to same packages
  g = []
  for t in text:
    t1 = t.strip('\n') 
    if 2 > len(t1):
      groups.append(g)
      g=[]
    else:
      g.append(t1)
  groups.append(g)
  if testlevel > 0:
    print(groups)


  newgroups = []
  newpackages = [] # packages in each new group
  newsizes = [] # sizes of each group
  print('# groups', len(groups))
  for g in groups:
    newg = []
    i = 1
    for r in g: # each row in g
      expanded = expandrow(r)
      if isinstance(expanded,str):
        newg.append(expanded)
      else:
        for e in expanded:
          newg.append(e)
      print('count ',i); i+=1;
    if 0 < len(newg): 
      newgroups.append(newg)
      print("newg: ")
      print(newg)
      p = findpackage((newg[0]).split(" "))
      newpackages.append(p)
      newsizes.append(len(newg))
      print("packages: ")
      print(p)
      print("newpackages: ")
      print(newpackages)
      print("sizes: ")
      print(newsizes)

  ind = findnewgrouporder(newpackages, newsizes)

  i = 1
  out = newgroups[ind[0]]
  while(i < len(ind)):
    print("newgroups " + str(ind[i]) + ":")
    print(newgroups[ind[i]])
    tmp = crossprodsel(out,newgroups[ind[i]])
    out = copy.deepcopy(tmp)
    print(ind[i],)
    i+=1

  for t in out:
    print(t)

  return out

def main(filename: str="foobar"):
  myfile=open(filename,"r")
  text=myfile.readlines()
  return reduce_config(text)



testlevel = 0 # raise the test level to print more
if __name__ == "__main__":
  #main("foobar2")
  # main("foobar")
  main("toto_full.txt")
