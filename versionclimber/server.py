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

from . import liquid

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
    def __init__(self, config_file, demandsupply=False):
        """ Initialisation of the server.
        TODO: Add port asargument.
        """
        YAMLEnv.__init__(self, config_file, demandsupply)
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind("tcp://*:50008")


    def monkey_patch(self, liquidparser, knowcaller=False):

        #works = self.works()
        #liquidparser.works = works

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

        if self.algo_demandsupply:
            packageversions, miniseries = self.monkey_patch(liquidparser)
        else:
            constraints, todolist = self.monkey_patch(liquidparser)


        ####### TODO #######
        while True:
            data = self.socket.recv()
            print(data)

            print('data are ', data)
            if not data: break
            fields = data.split(" ")
            print("fields are: ", fields)
            # format is slave number, opcode, args
            # opcodes can be 'requestwork' with argument last configindex tried
            #    -- response can be a new config or 'done'
            # 'updatestatus' with argument configindex and succeed(1) or fail(0)
            numpart= ((fields[0]).split(":"))[1]
            if fields[1] == 'requestwork':
               ret = liquidparser.requestwork(int(numpart), int(fields[2]))
               print('ret from requestwork: ', ret)
            if fields[1] == 'updatestatus':
               ret = liquidparser.updatestatus(int(numpart), int(fields[2]), int(fields[3]))
               print('ret from updatestatus: ', ret)
            if ret == 'Success':
               break
            print("return value: ", ret)
            print("~~~~~~~~")
            self.socket.send("%s " % (ret))


        #if self.pre_stage:
        #    status = sh(self.pre_stage)

        # try:
        #     if self.algo_demandsupply:
        #         # print("PackageVersions", packageversions) # log this
        #         # print("miniseries", miniseries) # log this
        #         endconfig = liquidparser.liquidclimber(miniseries, packageversions, anchor)

        #     else:
        #         endconfig = liquidparser.liquidclimber(constraints, todolist)
        #     # print liquidparser.memory
        # finally:
        #     self.restore()

        # if self.post_stage:
        #     # Activate the last configuration that works and then run the postb step.
        #     status = sh(self.post_stage)

        # res = []

        # if not self.algo_demandsupply:
        #     for k, v in six.iteritems(endconfig):
        #         pkg = self.int2pkg[k]
        #         res.append('(%s,%s)'%(self.int2pkg[k], self.commits[self.int2pkg[k]][v-1]))
        # else:
        #     res = endconfig

        # t1 = clock()
        # s = 'Total time in %f s\n'%((t1-tx).total_seconds())
        # if STAT_FILE:
        #     f = open(stat_file, 'a')
        #     f.write(s+'\n')
        #     f.close()
        # logger.info(s)

        return res

