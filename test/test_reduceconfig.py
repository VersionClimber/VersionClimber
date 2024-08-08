
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

# The idea is to take a cross product of pairs and then keep only those
# rows where the version numbers for the same package are the same.
# So if we take a cross-product between the first group and the second
# group and do the selection, we get
"""
P1__3 P2__4 P3__6 P2__4 P4__7
P1__3 P2__4 P3__6 P2__4 P4__8
P1__3 P2__4 P3__6 P2__4 P4__9
P1__4 P2__4 P3__6 P2__4 P4__7
P1__4 P2__4 P3__6 P2__4 P4__8
P1__4 P2__4 P3__6 P2__4 P4__9
"""
# Now take away the repeated elements in each row to get:
"""
P1__3 P2__4 P3__6 P4__7
P1__3 P2__4 P3__6 P4__8
P1__3 P2__4 P3__6 P4__9
P1__4 P2__4 P3__6 P4__7
P1__4 P2__4 P3__6 P4__8
P1__4 P2__4 P3__6 P4__9
"""
# Now join this result with the last group:
"""
P1__4 P2__4 P3__6 P4__7 P1__4 P6__1
P1__4 P2__4 P3__6 P4__8 P1__4 P6__1
P1__4 P2__4 P3__6 P4__9 P1__4 P6__1
P1__4 P2__4 P3__6 P4__7 P1__4 P6__2
P1__4 P2__4 P3__6 P4__8 P1__4 P6__2
P1__4 P2__4 P3__6 P4__9 P1__4 P6__2
"""
# Take away the repeats:
"""
P1__4 P2__4 P3__6 P4__7 P6__1
P1__4 P2__4 P3__6 P4__8 P6__1
P1__4 P2__4 P3__6 P4__9 P6__1
P1__4 P2__4 P3__6 P4__7 P6__2
P1__4 P2__4 P3__6 P4__8 P6__2
P1__4 P2__4 P3__6 P4__9 P6__2
"""

import copy

def crossprodsel(arr1, arr2):
  res = [sub1 + " " + sub2 for sub1 in arr1 for sub2 in arr2]
  out = []
  for r in res:
    sfields = r.split(" ")
    fields = [*set(sfields)] # remove duplicates
    fields.sort() 
    flag = 1 # no mismatch
    i = 1
    while ((i < len(fields)) and flag == 1):
      pair1 = fields[i].split("__") 
      pair2 = fields[i-1].split("__")
      if (pair1[0] == pair2[0]) and (not pair1[1] == pair2[1]):
        flag = 0
      i+= 1
    if flag == 1: 
     tmp = []
     for f in fields:
       tmp.append(f)
     out.append(' '.join(tmp))
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
    
# DATA


myfile=open("foobar","r")

# EXECUTION

text=myfile.readlines()
groups =[] # these will be groups of constraints
g = []
for t in text:
  t1 = t.strip('\n') 
  if 2 > len(t1):
    groups.append(g)
    g=[]
  else:
    g.append(t1)
groups.append(g)
print(groups)


newgroups = []
for g in groups:
  newg = []
  for r in g: # each row in g
    expanded = expandrow(r)
    if isinstance(expanded,str):
      newg.append(expanded)
    else:
      for e in expanded:
        newg.append(e)
  newgroups.append(newg)



i = 1
out = newgroups[0]
while(i < len(newgroups)):
  tmp = crossprodsel(out,newgroups[i])
  out = copy.deepcopy(tmp)
  i+=1

for t in out:
  print(t)
