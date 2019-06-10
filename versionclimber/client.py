""" Simple test for liquid VM

foo: healthy_head
goo: master
hoo : master
"""

from __future__ import absolute_import
from __future__ import print_function
import itertools
import logging

# import git
from .utils import sh, Path, new_stat_file, clock
from . import multigit
from .version import take, hversions, segment_versions
from .config import load_config, Package
import six
from six.moves import map
from six.moves import range
from six.moves import zip

from collections import OrderedDict

# Create a singleton defined once by the init method
# replace all that stuff with Objects.

logger = logging.getLogger(__name__)

STAT_FILE = False


class ClientEnv(YAMLEnv):
    """ Environment built from a YAML configuration file.

    Stages:
        - read the configuration
        - get locally the packages from git, svn or pypi
        - get the set of versions

    """
    def __init__(self, config_file, demandsupply=False, slaveid=0):
        """ Initialisation of the server.
        TODO: Add server ip address.
        """
        YAMLEnv.__init__(self, config_file, demandsupply)
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect("tcp://localhost:50008")
        self.slaveid = 0

    def install_config(self, semantic_config):
        """ Install a set of packages in the most atomic way.

        We will first install all the conda packages. Then use other commands separetly.
        """
        # TODO : Move the main code in a new object PackageSet

        #print(semantic_config) # log this
        pkg_names= list(semantic_config.keys())
        commits = list(semantic_config.values())
        pkgs =  [self.pkg_names[pn] for pn in pkg_names]
        versions = [commit for i, commit in enumerate(commits)]

        #print('versions', versions) # log this

        conda_pkgs = [(i, pkg) for i, pkg in enumerate(pkgs) if pkg.vcs == 'conda']
        other_pkgs = [(i, pkg) for i, pkg in enumerate(pkgs) if pkg.vcs != 'conda']

        status = 0
        if conda_pkgs:
            # channel
            channels = []
            for i, pkg in conda_pkgs:
                for c in pkg.conda_channels:
                    if c not in channels:
                        channels.append(c)

            channel_str = ' '.join(['-c '+ channel for channel in channels])

            cmd = 'conda install -y'
            for i, pkg in conda_pkgs:
                if len(pkg.cmd) > len(cmd):
                    # more options have been given in the command
                    cmd = pkg.cmd

            cmd_list = [cmd]
            cmd_list.append(channel_str)

            cmd_list.extend(['%s=%s' % (pkg.name, versions[i])
                             for i, pkg in conda_pkgs])
            cmd = ' '.join(cmd_list)

            t0 = clock()
            status = sh(cmd)
            t1 = clock()

            s = 'Run %s in %f s\n'%(cmd,(t1-t0).total_seconds())
            logger.info(s)
            if STAT_FILE:
                f.write(s)

            if status != 0:
                res = [False, 2, self.pkg2int[(conda_pkgs[0][1].name)],
                       self.pkg2int[self.universe[0]]]
                s = 'FAIL build %s\n'%cmd
                logger.info(s)
                if STAT_FILE:
                    f.write(s)
                    f.close()
                return status, res

        for i, pkg in other_pkgs:
            t0 = clock()
            commit = versions[i]
            python_ver = python_version(pkgs, versions)
            status = self.checkout(pkg, commit, python=python_ver)
            t1 = clock()
            s = 'Install (%s,%s) in %f s\n'%(pkg, commit,(t1-t0).total_seconds())
            logger.info(s)

            if status:
                res = [False, 2, self.pkg2int[pkg.name],
                       self.pkg2int[self.universe[0]]]
                return status, res


        return status, None

    def one_run(self):
        """ Run just the command in a fixed environment.

        Either the program fail, or it returns an error.
        """

        cmd = self.cmd

        status = sh(cmd)
        if Path(self.error_file).exists():
            if liquidparser.knowcaller:
                return parse_error(self.error_file)
            else:
                Path(self.error_file).move(curdir/'errors'/self.error_file+str(count))
                return -1, -1
        else:
            return status


    def works(self, log_dir='.'):
        """ Get the function that will be evaluated by the algorithm.

        Works take a set of versions, checkout each packages accordingly, and run a script.
        It returns the success or failure of it.
        """
        self.count = 0

        stat_file = new_stat_file(exp=log_dir)
        pkg_first= self.universe[0]

        install_errors = []

        def works_yaml(listofpackversions, stat_file=stat_file, env=self):
            env.count += 1
            count = env.count

            config = listofpackversions

            s = "\nConfiguration %d"%count
            logger.info(s)
            if STAT_FILE:
                f = open(stat_file, 'a')
                f.write(s+'\n')

            semantic_config = env.config2txt(config)

            s = ', '.join(['%s: %s'%(pkg, commit) for pkg, commit in six.iteritems(semantic_config)])
            logger.info(s)
            if s and STAT_FILE:
                f.write(s+'\n'+'\n')
                f.write('# Installation of packages'+'\n')

            logger.info('# Installation of packages')

            tx = clock()

            status, ret = env.install_config(semantic_config)
            if status and ret:
                return ret
            elif status:
                if STAT_FILE: f.close()
                res = [False, 2, -1, -1]
                return res

            t2 = clock()
            status = env.one_run()
            #status = 0

            t3 = clock()

            s = 'Configuration execution in %f s \n'%(t3-t2).total_seconds()
            logger.info(s)
            if STAT_FILE: f.write(s)

            if status:
                s = 'Execution FAILED\n'
                if STAT_FILE: f.write('Execution FAILED\n')
                logger.info('Status '+str(status))


            s = 'Total time: %f s\n'%(t3-tx).total_seconds()
            if STAT_FILE: f.write(s)
            logger.info(s)

            if STAT_FILE: f.close()

            if status == 0:
                res = [True, 0, -1, -1]
            else:
                try:
                    if liquidparser.knowcaller:
                        res = [False, 0, pkg2int[status[1]], pkg2int[status[0]]]
                    else:
                        res = [False, 2, -1, -1]
                except:
                    res = [False, 2, -1, -1]
            return res

        ###################################
        # Work function for the New algorithm demand supply

        def works_demandsupply(listofpackversions, stat_file=stat_file, env=self):
            env.count += 1
            count = env.count

            config = listofpackversions

            s = "\nConfiguration %d"%count
            logger.info(s)
            if STAT_FILE:
                f = open(stat_file, 'a')
                f.write(s+'\n')

            #semantic_config = env.config2txt(config)
            semantic_config = OrderedDict(config)

            s = ', '.join(['%s: %s'%(pkg, commit) for pkg, commit in config])
            logger.info(s)
            if s and STAT_FILE:
                f.write(s+'\n'+'\n')
                f.write('# Installation of packages'+'\n')

            logger.info('# Installation of packages')

            tx = clock()

            status, ret = env.install_config(semantic_config)
            if status:
                return False

            t2 = clock()
            status = env.one_run()
            #status = 0

            t3 = clock()

            s = 'Configuration execution in %f s \n'%(t3-t2).total_seconds()
            logger.info(s)
            if STAT_FILE: f.write(s)

            if status:
                s = 'Execution FAILED\n'
                if STAT_FILE: f.write('Execution FAILED\n')
                logger.info('Status '+str(status))


            s = 'Total time: %f s\n'%(t3-tx).total_seconds()
            if STAT_FILE: f.write(s)
            logger.info(s)

            if STAT_FILE: f.close()


            if status == 0:
                print("SUCCEED!!!!!!!!")
                # res = [True, 0, -1, -1]
                res = True
            else:
                res = False

            return res


        works_function = works_demandsupply if self.algo_demandsupply else works_yaml
        return works_function


    def monkey_patch(self, liquidparser, knowcaller=False):

        works = self.works()
        liquidparser.works = works

        if self.algo_demandsupply:
            #liquidparser.tryconfig = lambda c: 1
            return self._supply_constant_packages()

        else:
            universe = self.universe
            ordered_packages = universe

            sourcemap, default, todolist = variables_for_parser(ordered_packages, env=self)
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

    def restore(self):
        for pkg in self.pkgs:
            pkg.restore()

    def run(self, liquidparser, anchor=False):

        tx = clock()

        works = self.works()
        liquidparser.works = works

        if self.pre_stage:
            status = sh(self.pre_stage)

        #########################################
        # Client
        while True:
          print slaveidstring, "requestwork", currentindex
          socket.send(b'request:' + slaveidstring + 'requestwork ' + str(currentindex))
          data = socket.recv()
          print "master requests work on: ", data
          x = data.split(" ")
          print "x is: ", x
          currentindex = int(x[0])
          c = x[1]
          if x[2] == 'Tried_everything':
            print 'Wait for others'
          status = tryconfig(c)
          print 'status on configuration ', c, ' is: ', status
          socket.send(b'update:' + slaveidstring + 'updatestatus ' + str(currentindex) + ' ' + str(status))
          data = socket.recv()
          x = data.split(" ")
          print "return from updatestatus is: ", data
          if x[1] == 'Success':
            print 'configuration ', c, ' is a winner: '
            break

        #########################################

        # try:
        #     if self.algo_demandsupply:

        #     # print liquidparser.memory
        # finally:
        #     self.restore()


        # res = []

        res = []
        return res

