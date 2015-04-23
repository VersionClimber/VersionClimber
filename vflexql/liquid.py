""" Simple test for liquid VM

foo: healthy_head
goo: master
hoo : master
"""

import itertools
import git
from vflexql.utils import sh, path
from vflexql import multigit

# Create a singleton defined once by the init method
# replace all that stuff with Objects.

class Environment(object):
    empty = True

env = Environment()

def init(dir='simple', universe=('foo', 'goo', 'hoo')):
    """ Set a global variable """

    global env
    env.d = env.commits = multigit.universe_versions(dir, universe)
    env.universe = env.d.keys()
    env.curdir = path('.').abspath()

    env.pkg_dir = path(dir)

    env.branch_names = multigit.branch_names(env.pkg_dir)
    env.error_file = 'error.txt'
    env.empty = False

    # create here a virtual environment
    #activate()


#cmd = 'python simple/test.py'
#
def checkout(pkg, commit):
    d = env.pkg_dir / pkg
    d.chdir()

    commit = str(commit)

    sh('git checkout %s'%commit)

    env.curdir.chdir()

def pip_install(pkg, no_index=True):
    env.pkg_dir.chdir()
    if no_index:
        cmd = 'pip --isolated install --no-index --upgrade ./%s' % pkg
    else:
        cmd = 'pip --isolated install --upgrade ./%s' % pkg

    sh(cmd)
    env.curdir.chdir()

def master(pkg):
    name = env.branch_names[pkg]
    checkout(pkg, name)

def activate(dir=None):
    """ TODO
    """
    p = env.pkg_dir/'venv2/bin/activate_this.py'
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
        cmd = 'python %s' % (env.pkg_dir/'test.py')

    #sh('rm simple/*/*.pyc')
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

def experiment(pkgs=('foo', 'goo', 'hoo')):
    restore_config()
    gen = itertools.product(*[reversed(env.commits[pkg]) for pkg in pkgs])

    result = []
    for commits in gen:
        for pkg, commit in zip(pkgs, commits):
            checkout(pkg, commit)
            pip_install(pkg)
        
        # TODO: Add script path and name 
        status = run()

        res = ', '.join([pkg+'(%s)'%str(commit) for pkg, commit in zip(pkgs, commits)])
        if status == 0:
            result.append(res + ', OK')
        else: 
            result.append(res + ', FAILURE' +' (%s ,%s)'%(status[0], status[1]))

    restore_config()
    return '\n'.join(result)

