import zmq
from versionclimber import config, liquid, version
from versionclimber.algo import demandsupply
from message import Message

config_file = '../config.yaml'
cstream = open(config_file).read()
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:50008")



#########################################
# Configuration
#########################################

# Phase 1:
# For the first phase  assume we have a big array with configurations
# of anchors (and only anchors) in descending lexicographic order.
# So, lower indexes are lexicographically greater than later ones.
# Call that configarray.

# Phase 1.1: Compute this config array directly
#      This intermediate step is done in the server side (bad).
#      This will then implemented by a client.
#      Finally it can be done by all the clients (to test the speed up vs complexity)

####################################################################################
def retrieve_packages(conf):
    config = conf
    pkgs = config['packages']
    cmd = config['run']
    pre_stage = config['pre']
    post_stage = config['post']
    pkg_names = {pkg.name: pkg for pkg in self.pkgs}

    for pkg in pkgs:
        pkg.clone()

    _pkg_versions = {}
    for pkg in pkgs:
        tags = pkg.hierarchy != 'commit'
        vers = pkg.versions(tags=tags)
        _pkg_versions[pkg.name] = vers

    universe = [pkg.name for pkg in self.pkgs]

    init_config = {}
    for pkg in self.pkgs:
        init_config[pkg.name] = (pkg.version, pkg.hierarchy)

    commits = pkg_versions(universe, init_config, _pkg_versions, {})

    packageversions = [[[pkg.name, c] for c in commits[pkg.name]] for pkg in pkgs]

    miniseries = []
    for pkg in pkgs:
        versions = commits[pkg.name]
        # parametrise the extraction type for each package (major, minor, patch, commit)
        v_dict = version.segment_versions(versions, type=pkg.supply)
        for _version in v_dict:
            if pkg.name == 'python':
                miniseries.append([pkg.name, 'demand-constant', v_dict[_version]])
            else:
                miniseries.append([pkg.name, 'supply-constant', v_dict[_version]])

    return packageversions, miniseries


def findworkingminiseries(miniseries, anchor_config):
    """ find the working miniseries from a set of anchors.

    :TODO:
        - add the list of packages

    # CPL: Question: Do we select only one version for supply-constant?
    """
    out = []
    i = -1
    currentpackage = ''
    anchor = None
    new = []
    found = False

    for p in miniseries:
        pkgname, constant, versions = p
        if not pkgname == currentpackage:
            currentpackage = pkgname
            i+=1
            anchor = anchor_config[i]
            found = False
        elif pkgname == currentpackage and found:
            continue

        if anchor in versions:
            found = True
            out.append(versions)

    assert len(out) == len(anchor_config)
    return out

####################################################################################

"""
    data = socket.recv_pyobj()

    if data.category== 'request' and data.content == 'config':
        m = Message('send_config', cstream)
        socket.send_pyobj(m)

    print(conf['packages'])
    versions_to_compute = list(conf['packages'])
    n= len(versions_to_compute)
    versions = {}

    # Work todo
    while versions_to_compute:

        data = socket.recv_pyobj()
        if data.category == 'request':
            if data.content == 'work':
                pkg = versions_to_compute.pop()
                m = Message('request_version', pkg)
                socket.send_pyobj(m)
            elif data.content == 'config':
                m = Message('send_config', cstream)
                socket.send_pyobj(m)

    data = socket.recv_pyobj()
"""

STAGE = 1 # or 2

conf = config.load_config(config_file)

packageversions, miniseries = retrieve_packages(conf)
nb_configs, configs = demandsupply.genconfigs(miniseries, packageversions, anchorFlag=True)

configarray = list(configs)

# In addition we have an array of statuses that is of the same size
# and that is initialized to the value "undone".
statusarray = ['undone' for n in range(len(configarray))]
# Altogether there are three statuses: "undone", "success", "fail"

################# Dennis
# CPL: TODO Change the strategy to not have any index

# CPL: TODO Design a new API btw client / server
# CPL: 1. Request the configuration
# CPL: 2. Request work and send status
# CPL: 3. Die
currentindex = 0
foundbestanchor = False
successfound = False # if some slave returns success then this is set to True
successindex = 900000000 # index of lowest successful configuration
while (not foundbestanchor):
    data = socket.recv_pyobj()
    ret = None

    print(data)
    print('data are ', data)
    if not data:
        break
    print("Message content from client is: ", data.content)

    if data.category == "request_config":
        m = Message('send_config', conf)
        socket.send_pyobj(m)
        continue

    # CPL: Adapt to new message strategy
    # format is slave number, opcode, args
    # opcodes can be 'requestwork' with argument or -1
    # 'updatestatus' with arguments mini-series (-1 in first phase),
    # configindex and succeed(1) or fail(0)
    # numpart= ((fields[0]).split(":"))[1]
    if (data.category == 'request_work') and successfound:
        # Find anything lexicographically earlier has
        # not yet been done.
        # There must be something or the last statusupdate message
        # would have declared everything done.
        i = 0
        worktodo = False
        while (i < successindex):
            if statusarray[i] == "undone":
                worktodo = True
                # CPL : TODO: replace by an object
                ret = [-1, i, configarray[i]]
                # the intent is to give configuration i;
                # The -1 shows the absence of a mini-series for the first phase
                # CPL TODO: add logging for server
                print('ret from request_work: ', ret)
                break
            i+= 1

        assert worktodo == True

    # Otherwise would have left this first phase
    # when processing a status
    if (data.category == 'request_work') and not successfound:
        if (currentindex < len(configarray)):
            # Just send the next task in the configuration array
            ret = [-1, currentindex, configarray[currentindex]]
            print('ret from requestwork: ', ret)
            currentindex+= 1
        else:
            # Have no more configs to try start again
            currentindex = 0
            while (currentindex < len(configarray)) and (statusarray[currentindex] != "undone"):
                currentindex+= 1
            if (currentindex < len(configarray)):
                ret = [-1, currentindex, configarray[currentindex]]
            else:
                print('Have exhausted the configuration array without finding anything')
                # CPL TODO: error with indication of no configuration found

    # Status update will be given back slaveid, 'updatestatus', mini-series, index, and success/fail.
    if data.category == 'update_status':
        # CPL: TODO: rename variables / add objects
        client_miniserie, client_index, client_status = data.content

        ret = [client_index, client_status] # index and success/fail
        if client_status == 'success':
            statusarray[client_index] = 'success'
            # assumes first field of return is configindex
            successfound = True
            if (client_index < successindex):
                successindex = client_index
        if client_status != 'success':
            statusarray[client_index] = 'fail'

        if successfound:    # check whether there is more work to do
            i = 0
            worktodo = False
            while (i < successindex):
                if statusarray[i] == "undone":
                    worktodo = True
                    break
                i+= 1

            if not worktodo:
                foundbestanchor = True

            # successindex is the best
            # In this case we will go to the next loop.

    if data.category == 'request_work' and ret:
        print("return value: ", ret)
        print("~~~~~~~~")
        m = Message('send_work', ret)
        socket.send_pyobj(m)

###################################################################################
# Second Stage: Once best anchor is found look for optimal configuration

# successindex has the configuration containing the best working anchors
# We have an array
# workinganchors with the versions from each package of the workinganchors.
# corresponding to successindex. ?? Need Christophe
# Now we need a function that extracts the best working mini-series for each
# anchor. ?? Need Christophe: -- workingmini --
# workingmini = findworkingminiseries(successindex)

# CPL TODO: find working miniseries from anchors

# CPL
#workingmini = [[1,2,3], [2,3,4,5], [1,2,3,4,5]]
workingmini = findworkingminiseries(miniseries, configarray[successindex])

numpackages = len(workingmini)
miniseries = workingmini

# We also have an array of booleans called taketop which is True initially
# because we have to start by taking the top one and becomes False
# after our first optimistic foray.
taketop = [True for i in range(numpackages)]

# status for each package is 'available' means that this package has work to do
# other status is 'working' meaning a slave is doing something for this package
# 'found' meaning we've found the best version.
status = ['available' for i in range(numpackages)] # 'available, working, found'

# Finally, we have bestconfig also of length numpackages which will have
# the found version of each package.
# It is initially filled with the versions of the best anchor

# ??? Christophe
bestconfig = ['unknown' for i in range(numpackages)]
# CPL: fill with bestanchor
bestconfig = [configarray[successindex][i] for i in range(numpackages)]

# Whenever a response comes back, if success, then we put the result
# in bestconfig. If failure, we eliminate that config and all superior ones.

# CPL
# The formconfig function takes all working anchors except for
# the one for packageindex and builds a configuration from that
def formconfig(packageindex, newversion, bestconfig):
    return [v if i!=packageindex else newversion for i, v in enumerate(bestconfig)]


# Fill in the versions for packages where there is only one version
# If everything then we're done
# numberleft is the number of packages on which we need to do binary search

numberleft = 0
i = 0
while (i < numpackages):
    if len(miniseries[i]) == 1:
        bestconfig[i] = miniseries[i][0]
        status[i] = 'found'
    else:
        numberleft+= 1
    i+= 1

packageindex = 0
while numberleft > 0:
    data = socket.recv_pyobj()
    print(data)
    print('data are ', data)
    if not data:
        break
    print("Message content from client is: ", data.content)

    ret = None

    if data.category == "request_config":
        m = Message('send_config', conf)
        socket.send_pyobj(m)
        continue

    if data.category == "request_work":

    #fields = data.split(" ")
    #print("fields are: ", fields)
    #numpart= ((fields[0]).split(":"))[1]
    #if (fields[1] == 'requestwork'):
        packageindex = 0
        while (packageindex < numpackages) and (status[packageindex] != 'available'):
            packageindex+=1
        if (packageindex == numpackages):
            # nothing available but maybe something not found
            packageindex = 0
            while (packageindex < numpackages) and (status[packageindex] != 'found'):
                packageindex+=1

        if (packageindex < numpackages) and (taketop[packageindex] == True):
            taketop[packageindex] = False
            newconfig = formconfig(packageindex, miniseries[packageindex][-1], bestconfig)
            ret = [packageindex, -1, newconfig]
            status[packageindex] = 'working'
        # start with the top of the mini-series
        elif (packageindex < numpackages) and (taketop[packageindex] != True):
            mid = int(len(miniseries[packageindex])/2)
            newconfig = formconfig(packageindex, miniseries[packageindex][mid], bestconfig)
            ret = [packageindex, mid, newconfig]
            status[packageindex] = 'working'
        else:
            print("Should not reach this, because we would only if everything found and then we'd be done")

    # Status update will be given back slaveid, 'updatestatus', mini-series, index, and success/fail.
    if data.category == 'update_status':
        client_pkgindex, client_index, client_status = data.content
        #ret = [int(fields[2]), int(fields[3]), fields[4]]
        # mini-series, index, success/fail
        print('ret from updatestatus: ', data.content)
        if client_status == 'success':
            status[client_pkgindex] = 'found'
            bestconfig[client_pkgindex] = miniseries[client_pkgindex][client_index]
        else:
            miniseries[client_pkgindex] = miniseries[client_pkgindex][0:client_index]
            # truncate up to but not including that index
            if len(miniseries[client_pkgindex]) > 1:
                status[client_pkgindex] = 'available'
            else:
                status[client_pkgindex] = 'found'
                bestconfig[client_pkgindex] = miniseries[client_pkgindex][0]

    if data.category == 'request_work' and ret:
        print("return value: ", ret)
        print("~~~~~~~~")
        m = Message('send_work', ret)
        socket.send_pyobj(m)

    # recalculate numberleft
    i = 0
    numberleft = 0
    while(i < numpackages):
        if (status[i] != 'found'):
            numberleft+= 1
        i+= 1


