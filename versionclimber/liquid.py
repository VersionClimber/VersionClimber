""" Simple test for liquid VM

foo: healthy_head
goo: master
hoo : master
"""

import itertools
# import git
from .utils import sh, path, new_stat_file, clock
from . import multigit
from .version import take, hversions
from .config import load_config

# Create a singleton defined once by the init method
# replace all that stuff with Objects.


class Environment(object):
    empty = True

    def init(self, dir='simple', universe=('foo', 'goo', 'hoo'), Tags=False, endof=None):
        """ Set a global variable """

        self.d = self.commits = multigit.universe_versions(dir, universe, Tags=Tags)
        if endof:
            for pkg in endof:
                print 'DDD', self.d.keys()
                if pkg in self.d:
                    self.d[pkg].insert(0,endof[pkg])

        self.universe = self.d.keys()
        self.curdir = path('.').abspath()

        self.pkg_dir = path(dir)

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
        self.pkg2int = dict(zip(universe, range(1, n)))
        self.int2pkg = dict(zip(range(1, n), universe))

    def _convert_commits(self):
        """ Convert a list of commits to int

        The commits are a list from newer to later
        """
        commits = self.commits
        c2i2c = self.bidir_commits = {}
        for pkg, commit_list in commits.iteritems():
            n = len(commit_list) + 1
            cl = map(str, reversed(commit_list))
            c2i = dict(zip(cl, range(1, n)))
            i2c = dict(zip(range(1, n), cl))
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
    execfile(p, dict(__file__=p))


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
    execfile(p, dict(__file__=p))


def config(pkg_config):
    for pkg, commit in env.pkg_config.iteritems():
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
    src = str(path(filename).namebase)
    msg = '\n'.join(lines[1:])
    for pkg in env.universe:
        if pkg in msg:
            tgt = pkg
            break
        else:
            print msg
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
        dc = dict(zip(pkgs, commits))
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
    for pkg, commit_list in commits.iteritems():
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

        if iversion is None:
            commits = versions[pkg]
        else:
            commits = versions[pkg][versions[pkg].index(iversion):]

        if isinstance(commits[0], basestring) and ('r' == commits[0][0]):
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

'''
def _convert_commits(pkgs):
    """ Convert a list of commits to int

    The commits are a list from newer to later
    """
    commits = pkgs
    c2i2c = bidir_commits = {}
    for pkg, commit_list in commits.iteritems():
        n = len(commit_list) + 1
        cl = map(str, commit_list)
        c2i = dict(zip(cl, range(1, n)))
        i2c = dict(zip(range(1, n), cl))
        c2i2c[pkg] = c2i, i2c
    return bidir_commits
'''


class MyEnv(object):
    """ TODO: inherit of Environment before replacnig it...
    """
    empty = True

    def __init__(self, universe, versions):
        """ Set a global variable """

        self.d = self.commits = versions  # multigit.universe_versions(dir, universe, Tags=Tags)
        self.universe = universe
        # self.curdir = path('.').abspath()

        # self.pkg_dir = path(dir)

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
        self.pkg2int = dict(zip(universe, range(1, n)))
        self.int2pkg = dict(zip(range(1, n), universe))

    def _convert_commits(self):
        """ Convert a list of commits to int

        The commits are a list from newer to later
        """
        commits = self.commits
        c2i2c = self.bidir_commits = {}
        for pkg, commit_list in commits.iteritems():
            n = len(commit_list) + 1
            cl = map(str, commit_list)
            c2i = dict(zip(cl, range(1, n)))
            i2c = dict(zip(range(1, n), cl))
            c2i2c[pkg] = c2i, i2c

    def config2txt(self, config):
        semantic_config = {}
        int2pkg = self.int2pkg
        bidir = self.bidir_commits
        for pi, ci in config.iteritems():
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
    def __init__(self, config_file):
        self.pkgs, self.cmd = load_config(config_file)

        self.pkg_names = {pkg.name: pkg for pkg in self.pkgs}

        for pkg in self.pkgs:
            print('Get %s'%pkg)
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


    def checkout(self, pkg_name, commit):
        """

        """
        pkg = self.pkg_names[pkg_name]
        status = pkg.local_install(commit)
        return status


    def one_run(self):
        """ Run just the command in a fixed environment.

        Either the program fail, or it returns an error.
        """

        cmd = self.cmd

        status = sh(cmd)
        if path(error_file).exists():
            if liquidparser.knowcaller:
                return parse_error(error_file)
            else:
                path(error_file).move(curdir/'errors'/error_file+str(count))
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

        def works_yaml(listofpackversions, stat_file=stat_file, env=self):
            env.count += 1
            count = env.count

            config = listofpackversions

            f = open(stat_file, 'a')
            s = "\nConfiguration %d"%count
            print s
            f.write(s+'\n')

            semantic_config = env.config2txt(config)

            s = ', '.join(['%s: %s'%(pkg, commit) for pkg, commit in semantic_config.iteritems()])
            print s
            if s:
                f.write(s+'\n'+'\n')

            f.write('# Installation of packages'+'\n')

            tx = clock()

            for pkg, commit in semantic_config.iteritems():
                t0 = clock()
                status = env.checkout(pkg, commit)
                t1 = clock()
                s = 'Install (%s,%s) in %f s\n'%(pkg, commit,(t1-t0).total_seconds())
                print s
                f.write(s)
                if status != 0:
                    res = [False, 0, pkg2int[pkg], pkg2int[pkg_first]]
                    s = 'FAIL build %s\n'%pkg
                    f.write(s)
                    f.close()
                    return res

            t2 = clock()
            status = env.one_run()
            #status = 0

            t3 = clock()

            s = 'Configuration execution in %f s \n'%(t3-t2).total_seconds()
            f.write(s)
            print s

            if status:
                s = 'Execution FAILED\n'
                f.write('Execution FAILED\n')
                print 'Status ', status


            s = 'Total time: %f s\n'%(t3-tx).total_seconds()
            f.write(s)
            print s

            f.close()

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

        return works_yaml


    def monkey_patch(self, liquidparser, knowcaller=False):

        works = self.works()
        universe = self.universe

        liquidparser.works = works
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

    def run(self, liquidparser):
        constraints, todolist = self.monkey_patch(liquidparser)

        try:
            endconfig = liquidparser.liquidclimber(constraints, todolist)
            # print liquidparser.memory
        finally:
            self.restore()

        res = []
        for k, v in endconfig.iteritems():
            pkg = self.int2pkg[k]
            res.append('(%s,%s)'%(self.int2pkg[k], self.commits[self.int2pkg[k]][v-1]))


        return res
