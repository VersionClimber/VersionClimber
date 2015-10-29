""" Simple test for liquid VM

foo: healthy_head
goo: master
hoo : master
"""

from utils import sh, path
import itertools
import task3
import git

d = task3.universe_versions()

universe = d.keys()
curdir = path('.').abspath()

pkg_dir = path('simple')

branch_names = task3.branch_names()

cmd = 'python simple/test.py'
error_file = 'error.txt'

def checkout(pkg, commit):
    d = pkg_dir / pkg
    d.chdir()

    commit = str(commit)

    sh('git checkout %s'%commit)

    curdir.chdir()

def pip_install(pkg, no_index=True):
    pkg_dir.chdir()
    if no_index:
        cmd = 'pip --isolated install --no-index --upgrade ./%s' % pkg
    else:
        cmd = 'pip --isolated install --upgrade ./%s' % pkg

    sh(cmd)
    curdir.chdir()

def master(pkg):
    name = branch_names[pkg]
    checkout(pkg, name)

def activate():
    p = pkg_dir/'venv2/bin/activate_this.py'
    execfile(p, dict(__file__=p))

def config(pkg_config):
    for pkg, commit in pkg_config.iteritems():
        checkout(pkg, commit)

def restore_config():
    for pkg in branch_names:
        master(pkg)

def run(cmd=cmd, error_file=error_file):
    
    #sh('rm simple/*/*.pyc')
    status = sh(cmd)
    if status == 0:
        return status
    else:
        return parse_error(error_file)

def parse_error(error_file):
    s = open(error_file).read()
    lines = s.split('\n')
    lines = [l.strip() for l in lines if l.strip().startswith('File ')]
    lines = lines[-2:]
    filenames = [l.split(',')[0].split(' ')[-1].strip('"') for l in lines]
    pkgs = [str(path(f).namebase) for f in filenames]
    return pkgs

def experiment(pkgs=('foo', 'goo', 'hoo')):
    restore_config()
    gen = itertools.product(*[reversed(d[pkg]) for pkg in pkgs])

    result = []
    for commits in gen:
        for pkg, commit in zip(pkgs, commits):
            checkout(pkg,commit)
            pip_install(pkg)
        status = run()

        res = ', '.join([pkg+'(%s)'%str(commit) for pkg, commit in zip(pkgs, commits)])
        if status == 0:
            result.append(res + ', OK')
        else: 
            result.append(res + ', FAILURE' +' (%s ,%s)'%(status[0], status[1]))

    restore_config()
    return '\n'.join(result)

