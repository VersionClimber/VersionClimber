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


class Environment(object):
    empty = True

    def init(self, dir='simple', universe=('foo', 'goo', 'hoo'), Tags=False, endof=None):
        """ Set a global variable """

        self.d = self.commits = multigit.universe_versions(dir, universe, Tags=Tags)
        if endof:
            for pkg in endof:
                print('DDD', list(self.d.keys()))
                if pkg in self.d:
                    self.d[pkg].insert(0,endof[pkg])

        self.universe = list(self.d.keys())
        self.curdir = Path('.').abspath()

        self.pkg_dir = Path(dir)

        self.branch_names = multigit.branch_names(env.pkg_dir, universe)
        self.error_file = 'error.txt'
        self.empty = False

        self.conversion()

        # create here a virtual environment
        # activate()

    def conversion(self):
        self._convert_pkgname()
        self._convert_commits()

    def _convert_pkgname(self):
        """ Return 2 dict corresponding to package_name -> int
        and the reversed dict int -> package_name

        """
        universe = self.universe
        n = len(universe) + 1
        self.pkg2int = dict(list(zip(universe, list(range(1, n)))))
        self.int2pkg = dict(list(zip(list(range(1, n)), universe)))

    def _convert_commits(self):
        """ Convert a list of commits to int

        The commits are a list from newer to later
        """
        commits = self.commits
        c2i2c = self.bidir_commits = {}
        for pkg, commit_list in six.iteritems(commits):
            n = len(commit_list) + 1
            cl = list(map(str, reversed(commit_list)))
            c2i = dict(list(zip(cl, list(range(1, n)))))
            i2c = dict(list(zip(list(range(1, n)), cl)))
            c2i2c[pkg] = c2i, i2c


env = Environment()


# cmd = 'python simple/test.py'
#

def configure(dir, git_pkgs=[], svn_pkgs=[], pypi_pkgs=[]):
    pass


def init(dir='simple', universe=('foo', 'goo', 'hoo'), Tags=False):
    """ Factory method for environment initialisation.
    """
    env.init(dir=dir, universe=universe, Tags=Tags)


def checkout(pkg, commit):
    d = env.pkg_dir / pkg
    d.chdir()

    commit = str(commit)

    sh('git checkout %s' % commit)

    env.curdir.chdir()


def pip_install(pkg, no_index=True):
    env.pkg_dir.chdir()
    if no_index:
        cmd = 'pip install --no-index --upgrade ./%s' % pkg
    else:
        cmd = 'pip install --upgrade ./%s' % pkg

    sh(cmd)
    env.curdir.chdir()


def master(pkg):
    name = env.branch_names[pkg]
    checkout(pkg, name)


def activate(dir=None):
    """ TODO
    """
    p = env.pkg_dir / 'venv2/bin/activate_this.py'
    exec(compile(open(p).read(), p, 'exec'), dict(__file__=p))


def create_or_activate(dir=None):
    """ TODO
    """
    global env
    if dir is None:
        dir = env.pkg_dir

    dir.chdir()
    sh("virtualenv --always-copy venv")
    env.curdir.chdir()

    env.venv_dir = dir

    p = dir / 'venv/bin/activate_this.py'
    exec(compile(open(p).read(), p, 'exec'), dict(__file__=p))


def config(pkg_config):
    for pkg, commit in six.iteritems(env.pkg_config):
        checkout(pkg, commit)


def restore_config():
    for pkg in env.branch_names:
        master(pkg)


def run(cmd=None, error_file='error.txt'):
    if cmd is None:
        cmd = 'python %s' % (env.pkg_dir / 'test.py')

    # sh('rm simple/*/*.pyc')
    status = sh(cmd)
    if status == 0:
        return status
    elif env.knowcaller:
        return parse_error(error_file)
    else:
        return (-1, -1)


def parse_error(error_file):
    s = open(error_file).read()
    lines = s.split('\n')
    lines = [l.strip() for l in lines if l.startswith('  ')]
    n = len(lines)
    for i in range(n):
        if lines[-i - 1].strip().startswith('File '):
            break

    lines = lines[-i - 1:]
    l = lines[0]
    filename = l.split(',')[0].split(' ')[-1].strip('"')
    src = str(Path(filename).namebase)
    msg = '\n'.join(lines[1:])
    for pkg in env.universe:
        if pkg in msg:
            tgt = pkg
            break
        else:
            print(msg)
            tgt = ''
    return src, tgt


def experiment(pkgs=('foo', 'goo', 'hoo'), order_list=['hoo', 'goo', 'foo', 'hoo']):
    n = len(order_list)
    pkgi = env.pkg2int
    c2i = env.bidir_commits
    pairs = [(order_list[i], order_list[i + 1]) for i in range(n - 1)]

    restore_config()
    gen = itertools.product(*[reversed(env.commits[pkg]) for pkg in pkgs])

    result = []
    compatibilities = []

    for commits in gen:
        dc = dict(list(zip(pkgs, commits)))
        for pkg, commit in zip(pkgs, commits):
            checkout(pkg, commit)
            pip_install(pkg)

        # TODO: Add script path and name
        status = run()

        res = ', '.join(['%d' % (pkgi[pkg]) +
                         '(v %d)' % (c2i[pkg][0][str(commit)])
                         for pkg, commit in zip(pkgs, commits)])

        if status == 0:
            result.append(res + ', OK')
            for p1, p2 in pairs:
                c1, c2 = c2i[p1][0][str(dc[p1])], c2i[p2][0][str(dc[p2])]
                l = [pkgi[p1], c1, c1, pkgi[p2], c2, c2]
                compatibilities.append(l)
        else:
            result.append(res + ', FAILURE' + ' (%s ,%s)' % (status[0], status[1]))

    restore_config()
    return '\n'.join(result), compatibilities


def variables_for_parser(pkgs=('foo', 'goo', 'hoo'), default=None, env=env):
    """ Compute the main variables to call liquidparser

    :Parameters:
      - pkgs : the package names in a specific order

    :Returns:
        - sourcemap

    """
    commits = env.commits
    bidir_commits = env.bidir_commits
    p2i = env.pkg2int

    todolist = [p2i[p] for p in pkgs]

    sourcemap = {}
    _default = {}
    for pkg, commit_list in six.iteritems(commits):
        c2i, i2c = bidir_commits[pkg]
        cl = [c2i[str(commit)] for commit in commit_list]
        sourcemap[p2i[pkg]] = cl
        if default is None:
            _default[p2i[pkg]] = cl[0]
        else:
            _default[p2i[pkg]] = c2i[default[pkg]]

    return sourcemap, _default, todolist


##############################################################################
# Extended version
##############################################################################

def pkg_versions(universe, init_config, versions, endof=None):
    """ Extract a set of versions for each packages.

    The selection is computed based on initial information contains in init_config.

    :Example:
    ::
        universe = ('adel', 'mtg', 'caribu', 'rpy2')

        init_config = {}
        init_config['adel'] = ('r3417',0)
        init_config['caribu'] = ('r4122',0)
        init_config['mtg'] = ('r13066',0)
        init_config['rpy2'] = (u'2.5.1',0)

        # pkgs is a subset of versions
        pkgs = pkg_versions(universe, init_config, versions, endof)

    """
    pkgs = {}
    for pkg in universe:
        iversion = init_config[pkg][0]
        nb_versions = init_config[pkg][1]

        # Manage versions -x to select the x last commits.
        iversion = str(iversion) if iversion is not None else None


        if iversion is None:
            commits = versions[pkg]
        else:
            negative_version = (iversion[0]== '-') and iversion[1:].isdigit()

            if (iversion not in versions[pkg]) and negative_version:
                iversion = int(iversion)
                commits = versions[pkg][iversion:]
            else:
                commits = versions[pkg][versions[pkg].index(iversion):]

        if isinstance(commits[0], six.string_types) and ('r' == commits[0][0]):
            commits = [ci[1:] for ci in commits]
        pkgs[pkg] = commits

    for pkg in universe:
        nb_versions = init_config[pkg][1]
        commits = pkgs[pkg]

        if nb_versions in ('major', 'minor', 'patch'):
            commits = replace_by_wrong_commits(pkg, commits, endof)
            commits = hversions(commits, nb_versions)
        elif nb_versions == 'commit':
            pass
        elif nb_versions == 1:
                commits = [commits[0]]
        elif nb_versions == 2:
            commits = [commits[0], commits[-1]]
        else:
            if nb_versions > 2:
                commits = take(commits, nb_versions)
            commits = replace_by_wrong_commits(pkg, commits, endof)

        pkgs[pkg] = commits

    return pkgs


def replace_by_wrong_commits(pkg, commits, endof):
    """
    """
    if pkg in endof:
        wrong_commits = endof[pkg]
        n = len(wrong_commits)
        commits[-2 * n:-n], commits[-n:] = commits[-n:], wrong_commits

    return commits



class MyEnv(object):
    """ TODO: inherit of Environment before replacnig it...
    """
    empty = True

    def __init__(self, universe, versions):
        """ Set a global variable """

        self.d = self.commits = versions  # multigit.universe_versions(dir, universe, Tags=Tags)
        self.universe = universe
        # self.curdir = Path('.').abspath()

        # self.pkg_dir = Path(dir)

        # self.branch_names = multigit.branch_names(env.pkg_dir, universe)
        # self.error_file = 'error.txt'
        self.empty = False

        self.conversion()

        # create here a virtual environment
        # activate()

    def conversion(self):
        self._convert_pkgname()
        self._convert_commits()

    def _convert_pkgname(self):
        """ Return 2 dict corresponding to package_name -> int
        and the reversed dict int -> package_name

        """
        universe = self.universe
        n = len(universe) + 1

        if self.algo_demandsupply:
            self.int2pkg = self.pkg2int = dict(list(zip(universe, universe)))
        else:
            self.pkg2int = dict(list(zip(universe, list(range(1, n)))))
            self.int2pkg = dict(list(zip(list(range(1, n)), universe)))

    def _convert_commits(self):
        """ Convert a list of commits to int

        The commits are a list from newer to later
        """
        commits = self.commits
        c2i2c = self.bidir_commits = {}

        if self.algo_demandsupply:
            for pkg, commit_list in six.iteritems(commits):
                n = len(commit_list) + 1
                cl = list(map(str, commit_list))
                i2c = c2i = dict(list(zip(cl, cl)))
                c2i2c[pkg] = c2i, i2c

        else:
            for pkg, commit_list in six.iteritems(commits):
                n = len(commit_list) + 1
                cl = list(map(str, commit_list))
                c2i = dict(list(zip(cl, list(range(1, n)))))
                i2c = dict(list(zip(list(range(1, n)), cl)))
                c2i2c[pkg] = c2i, i2c

    def config2txt(self, config):
        semantic_config = {}

        int2pkg = self.int2pkg
        bidir = self.bidir_commits
        for pi, ci in six.iteritems(config):
            pkg = int2pkg[pi]
            commit = bidir[pkg][1][ci]
            semantic_config[pkg] = commit
        return semantic_config

###############################################################################

class YAMLEnv(MyEnv):
    """ Environment built from a YAML configuration file.

    Stages:
        - read the configuration
        - get locally the packages from git, svn or pypi
        - get the set of versions

    """
    def __init__(self, config_file, demandsupply=False):
        config = load_config(config_file)
        self.pkgs = config['packages']
        self.cmd = config['run']
        self.pre_stage = config['pre']
        self.post_stage = config['post']

        self.algo_demandsupply = demandsupply

        if isinstance(self.cmd, list):
            self.cmd = self.cmd[0]

        self.pkg_names = {pkg.name: pkg for pkg in self.pkgs}

        for pkg in self.pkgs:
            logger.info('Get %s'%pkg)
            pkg.clone()

        _pkg_versions = {}
        for pkg in self.pkgs:
            tags = pkg.hierarchy != 'commit'
            vers = pkg.versions(tags=tags)
            _pkg_versions[pkg.name] = vers

        universe = self.universe = [pkg.name for pkg in self.pkgs]

        init_config = {}
        for pkg in self.pkgs:
            init_config[pkg.name] = (pkg.version, pkg.hierarchy)

        # retrieve for each package (e.g. numpy, scipy, ...) the set of versions
        _pkgs = pkg_versions(universe, init_config, _pkg_versions, {})
        MyEnv.__init__(self, universe, _pkgs)

        self.knowcaller = False
        self.error_file = 'error.txt'


    def checkout(self, pkg_name, commit):
        """ Install the package `pkg_name` at a given version.

        """
        if isinstance(pkg_name, Package):
            pkg = pkg_name
            pkg_name = pkg.name
        else:
            pkg = self.pkg_names[pkg_name]
        version = self.bidir_commits[pkg_name][0][commit]
        status = pkg.local_install(commit,version=version)
        return status

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
            status = self.checkout(pkg, commit)
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

        if self.algo_demandsupply:
            packageversions, miniseries = self.monkey_patch(liquidparser)
        else:
            constraints, todolist = self.monkey_patch(liquidparser)

        if self.pre_stage:
            status = sh(self.pre_stage)

        try:
            if self.algo_demandsupply:
                # print("PackageVersions", packageversions) # log this
                # print("miniseries", miniseries) # log this
                endconfig = liquidparser.liquidclimber(miniseries, packageversions, anchor)

            else:
                endconfig = liquidparser.liquidclimber(constraints, todolist)
            # print liquidparser.memory
        finally:
            self.restore()

        if self.post_stage:
            # Activate the last configuration that works and then run the postb step.
            status = sh(self.post_stage)

        res = []

        if not self.algo_demandsupply:
            for k, v in six.iteritems(endconfig):
                pkg = self.int2pkg[k]
                res.append('(%s,%s)'%(self.int2pkg[k], self.commits[self.int2pkg[k]][v-1]))
        else:
            res = endconfig

        t1 = clock()
        s = 'Total time in %f s\n'%((t1-tx).total_seconds())
        if STAT_FILE:
            f = open(stat_file, 'a')
            f.write(s+'\n')
            f.close()
        logger.info(s)

        return res

    def _supply_constant_packages(self):
        """ Return a list of supply constant versions of the different packages. """

        if self.algo_demandsupply:
            # packageversions = [ [[p1, v1], [p1, v2]], [[p2, v1], [p2, v2]], ... ]
            # miniseries = [[p1, 'supply-constant', [v1, v2, ...] ], [p2, 'demand-constant', [] ] ]
            packageversions = [[[pkg.name, c] for c in self.commits[pkg.name]] for pkg in self.pkgs]

            # CPL TODO : to improve in a more generic way
            miniseries = []
            for pkg in self.pkgs:
                versions = self.commits[pkg.name]
                # parametrise the extraction type for each package (major, minor, patch, commit)
                v_dict = segment_versions(versions, type=pkg.supply)
                for _version in v_dict:
                    if pkg.name == 'python':
                        miniseries.append([pkg.name, 'demand-constant', v_dict[_version]])
                    else:
                        miniseries.append([pkg.name, 'supply-constant', v_dict[_version]])

            return packageversions, miniseries


    def print_versions(self, liquidparser=None):
        """ Print all the versions of the different packages."""

        print("-"*80)

        if liquidparser:
            nb_configs = self.number_of_configurations(liquidparser, anchor=False)
            print("Number of configurations potentially to explore: %d "%(nb_configs))

            nb_configs = self.number_of_configurations(liquidparser, anchor=True)
            print("Number of anchors to explore: %d "%(nb_configs))

        versions = self.commits
        if not self.algo_demandsupply:

            pkg_names = [pkg.name for pkg in self.pkgs]
            print("Versions of", ' '.join(pkg_names))
            for name in pkg_names:
                print('\n')
                print('Versions of ', name)
                print('-'*(12+len(name)))
                print('\n'.join(versions[name]))
        else:
            pkg_names = [pkg.name for pkg in self.pkgs]
            print("Versions of", ' '.join(pkg_names))
            for pkg in self.pkgs:
                name = pkg.name
                print('\n')
                print('Versions of ', name)
                print('-'*(12+len(name)))
                print('\n'.join(versions[name]))

                # parametrise the extraction type for each package (major, minor, patch, commit)
                v_dict = segment_versions(versions[name], type=pkg.supply)
                print('\n')
                print('Supply-constant Versions of ', name)
                print('-'*(12+len(name)))
                for _version in v_dict:
                    constant = 'Supply-constant ' if name != 'python' else 'Demand-constant '
                    print(constant, ' '.join(v_dict[_version]))



    def number_of_configurations(self, liquidparser, anchor=False, constraints=None):
        ""
        if self.algo_demandsupply:
            packageversions, miniseries = self.monkey_patch(liquidparser)

            if not constraints:
                constraints = {}
            versions = []
            for pkg in packageversions:
                if pkg[0][0] not in constraints:
                    versions.append(pkg)
                    continue
                name = pkg[0][0]
                v = constraints[name]
                for i, p in enumerate(pkg):
                    if p[1] == v:
                        versions.append(pkg[i:])
                        continue

            packageversions = versions

            nb_configs, configs = liquidparser.genconfigs(miniseries, packageversions, anchor)

            return nb_configs
