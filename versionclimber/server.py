""" Simple test for liquid VM

foo: healthy_head
goo: master
hoo : master
"""

from __future__ import absolute_import
from __future__ import print_function

from exceptions import NotImplementedError
# Used for the client server implementation
import zmq

from .liquid import YAMLEnv
from .utils import sh, Path, new_stat_file, clock

# Create a singleton defined once by the init method
# replace all that stuff with Objects.

###############################################################################

class ServerEnv(YAMLEnv):
    """ Environment built from a YAML configuration file.

    Stages:
        - read the configuration
        - get locally the packages from git, svn or pypi
        - get the set of versions

    """
    def __init__(self, config_file, demandsupply=False, debug=True):
        """ Initialisation of the server.
        TODO: Add port as argument.
        """
        if not debug:
            YAMLEnv.__init__(self, config_file, demandsupply)
        self.debug = debug
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind("tcp://*:50008")


    def monkey_patch(self, liquidparser, knowcaller=False):

        #works = self.works()
        #liquidparser.works = works
        # CPL : HACK
        if self.debug:
            return

        if self.algo_demandsupply:
            #liquidparser.tryconfig = lambda c: 1
            return self._supply_constant_packages()

        else:
            universe = self.universe
            ordered_packages = universe

            sourcemap, default, todolist = liquid.variables_for_parser(ordered_packages, env=self)
            orderofpackages = [self.pkg2int[p] for p in ordered_packages]

            liquidparser.compatibilities = []
            liquidparser.orderofpackages = orderofpackages
            liquidparser.default = default
            liquidparser.sourcemap = sourcemap
            liquidparser.strongmemory = []
            constraints = {}
            liquidparser.todolist = todolist
            liquidparser.knowcaller = knowcaller

            return constraints, todolist


    def run(self, liquidparser, anchor=False):

        tx = clock()

        if not self.debug:

            if self.algo_demandsupply:
                packageversions, miniseries = self.monkey_patch(liquidparser)
            else:
                constraints, todolist = self.monkey_patch(liquidparser)


        ######################################
        ####### ALGORITHM ####################
        ######################################

        encode_config = lambda c: ','.join(map(str,c))
        MAX_EX = 0

        # configarray is the set of miniseries (call this miniseries?)
        configarray = []
        configarray = [['highconfig'], ['midconfig'], ['lowconfig']]
        configarray = [[3,3,3], [2,2,2], [1, 1, 1] ]
        # CPL: generate configarray (client vs server).

        # In addition we have an array of statuses that is of the same size
        # and that is initialized to the value "undone".
        # Altogether there are three statuses: "undone", "success", "fail"
        # CPL: define status based on a kind of enum
        statusarray = ['undone' for n in range(len(configarray))]

        currentindex = 0
        foundbestanchor = False
        successfound = False # if some slave returns success then this is set to True
        successindex = float('inf') # index of lowest successful configuration

        # CPL info :
        #FORMAT fields (from client) and ret (to client)
        # slave number, opcode ('requestwork' or 'updatestatus')
        #  - requestwork : nothing
        #  - updatestatus : mini-series, index, and success/fail

        while (not foundbestanchor):
            data = self.socket.recv()
            if not data: break
            print('data are ', data)

            fields = data.split(" ")
            print("fields are: ", fields)
            # format is slave number, opcode, args
            # opcodes can be 'requestwork' with argument or -1
            # 'updatestatus' with arguments mini-series (-1 in first phase),
            # configindex and succeed(1) or fail(0)
            # numpart= ((fields[0]).split(":"))[1]
            if fields[1] == 'requestwork' and successfound:
              # Find anything lexicographically earlier has
              # not yet been done.
              # There must be something or the last statusupdate message
              # would have declared everything done.
              i = 0
              worktodo = False
              while (i < successindex):
                if statusarray[i] == "undone":
                  worktodo = True
                  ret = [-1, i, encode_config(configarray[i])]
                  # the intent is to give configuration i;
                  # The -1 shows the absence of a mini-series for the first phase
                  print('ret from requestwork: ', ret)
                  break
                i+= 1
              assert worktodo == True
              # Otherwise would have left this first phase
              # when processing a status
            if fields[1] == 'requestwork' and not successfound:
              # CPL: compute the number of configurations without storing them
              if (currentindex < len(configarray)):
                # Just send the next task in the configuration array
                ret = [-1, currentindex, encode_config(configarray[currentindex])]
                print('ret from requestwork: ', ret)
                currentindex+= 1
              else:
                # Have no more configs to try start again
                currentindex = 0
                while (currentindex < len(configarray)) and (statusarray[currentindex] != "undone"):
                  currentindex+= 1
                if (currentindex < len(configarray)):
                  ret = [-1, currentindex, encode_config(configarray[currentindex])]
                else:
                  print('Have exhausted the configuration array without finding anything')
                  # CPL: ?? Christophe: error with indication of no configuration found
                  if MAX_EX == 0:
                    return

            # Status update will be given back slaveid, 'updatestatus', ?mini-series?, index, and success/fail.
            # CPL: Up for now, miniseries are not sent back
            if fields[1] == 'updatestatus':
              # CPL: without miniseries, we replace 3 and 4 by 2 and 3
              ret = [int(fields[2]), int(fields[3]), fields[4]] # index and success/fail
              r_package, r_index, r_status = ret[0], ret[1], ret[2]
              if r_status == 'Success':
                statusarray[r_index] = 'success'
                   # assumes first field of return is configindex
                successfound = True
                if (r_index < successindex):
                  successindex = r_index
              if r_status != 'Success':
                statusarray[r_index] = 'fail'
              if successfound: # check whether there is more work to do
                i = 0
                worktodo = False
                while (i < successindex):
                  if statusarray[i] == "undone":
                    worktodo = True
                  i+= 1
                if not worktodo:
                  foundbestanchor = True
                  # successindex is the best
                  # In this case we will go to the next loop.

            # CPL NEW: does we need that?
            ret_msg = ' '.join(map(str, ret))
            print("return value: ", ret_msg)
            print("~~~~~~~~")
            self.socket.send("%s " % (ret_msg))

        ######################################
        ####### SECOND PHASE #################
        ######################################

        # successindex has the configuration containing the best working anchors
        # We have an array
        # workinganchors with the versions from each package of the workinganchors.
        # corresponding to successindex. ?? Need Christophe
        # Now we need a function that extracts the best working mini-series for each
        # anchor. ?? Need Christophe.
        # workingmini = findworkingminiseries(successindex)

        # CPL
        miniseries = workingmini = [[1,2,3], [2,3,4,5], [1,2,3,4,5]]

        numpackages = len(workingmini)

        # We also have an array of booleans called taketop which is True initially
        # because we have to start by taking the top one and becomes False
        # after our first optimistic foray.
        taketop = [True for i in range(numpackages)]
        # status for each package is 'available' means that this package has work to do
        # other status is 'working' meaning a slave is doing something for this package
        # 'found' meaning we've found the best version.
        status = ['available' for i in range(numpackages)]

        # Finally, we have bestconfig also of length numpackages which will have
        # the found version of each package.
        # It is initially filled with the versions of the best anchor
        # ??? Christophe
        # CPL TODO: set it correctly based on how you compute the miniseries
        bestconfig = [workingmini[i][0] for i in range(numpackages)]

        # Whenever a response comes back, if success, then we put the result
        # in bestconfig. If failure, we eliminate that config and all superior ones.

        # Fill in the versions for packages where there is only one version
        # If everything then we're done
        # numberleft is the number of packages on which we need to do binary search

        # CPL TODO: formconfig
        # TODO: CPL
        # The formconfig function takes all working anchors except for
        # the one for packageindex and builds a configuration from that

        # assemble a configuration from cand at position j of bestconfig
        def formconfig(j, cand, bestconfig=bestconfig):
            myconfig = []
            for i in range(numpackages):
                if (i == j):
                    myconfig.append(cand)
                else:
                    myconfig.append(bestconfig[i])
                i+= 1


            return encode_config(myconfig)


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
          data = self.socket.recv()
          print(data)
          print('data are ', data)
          if not data: break
          fields = data.split(" ")
          print("fields are: ", fields)
          numpart= ((fields[0]).split(":"))[1]
          if (fields[1] == 'requestwork'):
            packageindex = 0
            while (packageindex < numpackages) and (status[packageindex] != 'available'):
              packageindex+=1
            if (packageindex == numpackages):
              # nothing available but maybe something not found
              # CPL: infinite loop : check the config that has not been visited only.
              packageindex = 0
              while (packageindex < numpackages) and (status[packageindex] != 'found'):
                packageindex+=1
            # TODO: CPL
            # The formconfig function takes all working anchors except for
            # the one for packageindex and builds a configuration from that
            if (packageindex < numpackages) and (taketop[packageindex] == True):
              taketop[packageindex] = False
              ret = [packageindex, -1, formconfig(packageindex, miniseries[packageindex][-1])]
              status[packageindex] = 'working'
              # start with the top of the mini-series
            elif (packageindex < numpackages) and (taketop[packageindex] != True):
              mid = int(len(miniseries[packageindex])/2)
              ret = [packageindex, mid, formconfig(packageindex, miniseries[packageindex][mid])]
              status[packageindex] = 'working'
            else:
              print("Should not reach this, because we would only if everything found and then we'd be done")

          # Status update will be given back slaveid, 'updatestatus', mini-series, index, and success/fail.
          if fields[1] == 'updatestatus':

            ret = [int(fields[2]), int(fields[3]), fields[4]]
            # CPL modif
            #ret = [-1, int(fields[2]), fields[3]] # index and success/fail
            r_packageindex, r_index, r_status = ret
            # mini-series, index, success/fail
            print('ret from updatestatus: ', ret)
            if r_status == 'Success':
             status[r_packageindex] = 'found'
             bestconfig[ret[0]] = miniseries[ret[0]][ret[1]]
             miniseries[ret[0]] = miniseries[ret[0]][ret[1]:]
             if len(miniseries[ret[0]]) > 1:
               status[ret[0]] = 'available'
             else:
               status[ret[0]] = 'found'

            else:
             miniseries[ret[0]] = miniseries[ret[0]][0:ret[1]]
             # truncate up to but not including that index
             if len(miniseries[ret[0]]) > 1:
               status[ret[0]] = 'available'
             else:
               status[ret[0]] = 'found'
               bestconfig[ret[0]] = miniseries[ret[0]][0]
            print('MINISERIES: ', miniseries)

          # recalculate numberleft
          i = 0
          numberleft = 0
          while(i < numpackages):
           if (status[i] != 'found'):
             numberleft+= 1
           i+= 1

          # send the msg to client
          ret_msg = ' '.join(map(str, ret))
          print("Send message to client (332L): ", ret_msg)
          print("~~~~~~~~")
          self.socket.send("%s " % (ret_msg))

        print('*'*80)
        print('status: ', status)
        # Confirmation: So now we have numberleft == 0
        # Test bestconfig and if that doesn't succeed, replace bestconfig
        # with workingnchors.
        # Bestconfig will work if we were right about supplyconstant etc

        data = self.socket.recv()
        print(data)
        print('data are ', data)
        if not data: return
        fields = data.split(" ")
        print("fields are: ", fields)
        numpart= ((fields[0]).split(":"))[1]
        if (fields[1] == 'updatestatus'):
         # Status update will be given back slaveid, 'updatestatus', mini-series, index, and success/fail.
         ret = [int(fields[2]), int(fields[3]), fields[4]]
         if (ret[0] == -1): # this is the test on bestconfig
           if ret[2] == 'Success':
             print('Best config is: ' + bestconfig)
           else:
             print('Best config is: ' + miniseries)
        if (fields[1] == 'requestwork'):
          ret = [-1, -1, encode_config(bestconfig)]

        ret_msg = ' '.join(map(str, ret))
        print("Send message to client (362): ", ret_msg)
        print("~~~~~~~~")
        self.socket.send("%s " % (ret_msg))


        ######################################

        # while True:
        #     data = self.socket.recv()
        #     print(data)

        #     print('data are ', data)
        #     if not data: break
        #     fields = data.split(" ")
        #     print("fields are: ", fields)
        #     # format is slave number, opcode, args
        #     # opcodes can be 'requestwork' with argument last configindex tried
        #     #    -- response can be a new config or 'done'
        #     # 'updatestatus' with argument configindex and succeed(1) or fail(0)
        #     numpart= ((fields[0]).split(":"))[1]
        #     if fields[1] == 'requestwork':
        #        ret = liquidparser.requestwork(int(numpart), int(fields[2]))
        #        print('ret from requestwork: ', ret)
        #     if fields[1] == 'updatestatus':
        #        ret = liquidparser.updatestatus(int(numpart), int(fields[2]), int(fields[3]))
        #        print('ret from updatestatus: ', ret)
        #     if ret == 'Success':
        #        break
        #     print("return value: ", ret)
        #     print("~~~~~~~~")
        #     self.socket.send("%s " % (ret))




        return [bestconfig]

