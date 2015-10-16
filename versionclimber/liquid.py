""" Simple test for liquid VM

foo: healthy_head
goo: master
hoo : master
"""

import itertools
# import git
from utils import sh, path
import multigit

# Create a singleton defined once by the init method
# replace all that stuff with Objects.


class Environment(object):
    empty = True

    def init(self, dir='simple', universe=('foo', 'goo', 'hoo'), Tags=False):
        """ Set a global variable """

        self.d = self.commits = multigit.universe_versions(dir, universe, Tags=Tags)
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

    p = dir/'venv/bin/activate_this.py'
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
    else:
        return parse_error(error_file)


def parse_error(error_file):
    s = open(error_file).read()
    lines = s.split('\n')
    lines = [l.strip() for l in lines if l.startswith('  ')]
    n = len(lines)
    for i in range(n):
        if lines[-i-1].strip().startswith('File '):
            break

    lines = lines[-i-1:]
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
    pairs = [(order_list[i], order_list[i+1]) for i in range(n-1)]

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
            result.append(res + ', FAILURE' +' (%s ,%s)'%(status[0], status[1]))

    restore_config()
    return '\n'.join(result), compatibilities


def variables_for_parser(pkgs=('foo', 'goo', 'hoo'), default=None):
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
        cl = [c2i[str(commit)] for commit in reversed(commit_list)]
        sourcemap[p2i[pkg]] = cl
        if default is None:
            _default[p2i[pkg]] = cl[0]
        else:
            _default[p2i[pkg]] = c2i[default[pkg]]

    return sourcemap, _default, todolist
