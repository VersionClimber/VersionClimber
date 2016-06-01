"""
How to use Version Climber in a real life

TODO:
- Create a YAML environment with a list of packages
    * load_config
    * clone the packages
    * get the set of versions
    * select a subset of versions based on the hierarchy
    * build a bidirectional mapping for correspondance between liquidparser
    and the real life
- Create a run function to the env
- write a generic works function
- Monkey patch liquidparser
- Run the Horrible Thing
"""

###############################################################################
# User defined variables

# see params.py
"""
knowcaller = False
universe = ('mtg', 'adel', 'caribu', 'rpy2')

init_config = {}
init_config['adel'] = ('r3417',0)
init_config['caribu'] = ('r4122',0)
init_config['mtg'] = ('r13066',0)
init_config['rpy2'] = (u'2.5.1',0)

endof = {}


universe = ('mtg', 'adel', 'caribu', 'rpy2')

init_config = {}
init_config['adel'] = ('r3417',0)
init_config['caribu'] = ('r4122',0)
init_config['mtg'] = ('r13066',0)
init_config['rpy2'] = (u'2.5.1',0)
"""
###############################################################################
# Imports


import git
import versionclimber
from versionclimber import liquid, config
from versionclimber.utils import sh, path, pypi_versions, git_versions, svn_versions

###############################################################################
# Load config

config_file = 'config.yaml'

pkgs, cmd = config.load_config(config_file)
print map(str, pkgs)

###############################################################################
# Create a Virtual Env
# TODO
#os.system('source climber1/bin/activate')

###############################################################################
# Get the packages from their git repository
# TODO: Pull when already download
for pkg in pkgs:
    print('Get %s'%pkg)
    pkg.clone()

###############################################################################
# Access to the whole set of versions of the experiment

pkg_versions = {}
for pkg in pkgs:
    vers = pkg.versions()
    pkg_versions[pkg.name] = vers

# Check validity of the default version of each package.

universe = [pkg.name for pkg in pkgs]

print(pkg_versions)

init_config = {}
for pkg in pkgs:
    init_config[pkg.name] = (pkg.version, pkg.hierarchy)

# retrieve for each package (e.g. numpy, scipy, ...) the set of versions
_pkgs = liquid.pkg_versions(universe, init_config, pkg_versions, {})
env = liquid.MyEnv(universe, _pkgs)

# Alias
pkg2int = env.pkg2int  # dict(zip(universe, range(1, len(universe)+1)))
int2pkg = env.int2pkg  # dict(zip(pkg2int.values(), pkg2int.keys()))
bidir = env.bidir_commits  # _convert_commits(pkgs)






"""
pessimistic = False
if pessimistic:
    from versionclimber import liquidparser_pessimistic as liquidparser
else:
    from versionclimber import liquidparser


# Specific imports
import datetime
import subprocess
import pickle


###############################################################################
# Access to the whole set of versions of the experiment
# TODO: Code to compute them


f = open('versions.pkl')
versions = pickle.load(f)

###############################################################################
# Define the universe, the type of vcs repository
# Set an initial working configuration: init_config
# Setup the environment
###############################################################################



repos = {}
repos['adel'] = 'svn'
repos['caribu'] = 'svn'
repos['mtg'] = 'svn'
repos['rpy2'] = 'pypi'
repos['pandas'] = 'pypi'



pkgs = liquid.pkg_versions(universe, init_config, versions, endof)

env = liquid.MyEnv(universe, pkgs)

###############################################################################
# Script Execution
###############################################################################

# Where?
curdir = path('.').abspath()
pkg_dir = curdir


# Alias
pkg2int = env.pkg2int  # dict(zip(universe, range(1, len(universe)+1)))
int2pkg = env.int2pkg  # dict(zip(pkg2int.values(), pkg2int.keys()))
bidir = env.bidir_commits  # _convert_commits(pkgs)

###############################################################################
# Usefuff methods
###############################################################################

# TODO: remove all the side effects

def clock():
    return datetime.datetime.now()

def checkout_vcs(pkg, commit, vcs='git', pkg_dir=pkg_dir):
    d = pkg_dir / pkg
    d.chdir()

    commit = str(commit)
    if vcs == 'svn':
        sh('svn update -r %s'%commit)
    elif vcs == 'git':
        sh('git checkout %s'%commit)
    curdir.chdir()


def checkout(pkg, commit, repos=repos):
    vcs = repos[pkg]
    status = 0
    if vcs in ('svn', 'git'):
        checkout_vcs(pkg, commit, vcs=vcs)
        status = sh('pip install --no-index --no-deps -U ./%s'%pkg)
    else:
        status = sh('pip install -U %s==%s'%(pkg,commit))
    return status


def restore(**config):
    for pkg in config:
        if repos[pkg] == 'svn':
            checkout_vcs(pkg, 'HEAD', 'svn')
        elif repos[pkg] == 'git':
            checkout_vcs(pkg, 'master', 'git')


def run(cmd=None, error_file='error.txt', curdir=curdir):
    if cmd is None:
        cmd = 'ipython %s' % (curdir/'test_adel.py')

    #sh('rm simple/*/*.pyc')
    status = sh(cmd)
    if path(error_file).exists():
        if liquidparser.knowcaller:
            return parse_error(error_file)
        else:
            path(error_file).move(curdir/'errors'/error_file+str(count))
            return -1, -1
    else:
        return status


def parse_error(error_file):
    if not path(error_file).exists():
        return 'adel', 'caribu'

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
    for pkg in universe:
        if pkg in msg:
            tgt = pkg
            break
        else:
            print msg
            tgt = ''

    path(error_file).move(curdir/'errors'/error_file+str(count))

    if src in universe and tgt in universe:
        return src, tgt
    else:
        return 'mtg', 'adel'


def test(**config):
    print config

    # install
    t0 = clock()
    for pkg, commit in config.iteritems():
        checkout(pkg, commit)
    t1 = clock()
    print 'install in %f s' % (t1 - t0).total_seconds()
    # run Adel

    t2 = clock()
    status = run()
    t3 = clock()
    print 'run in %f s'%(t3-t2).total_seconds()
    print 'total time: %f s'%(t3-t0).total_seconds()

    if status != 0:
        print 'FAILURE ', config, status
    else:
        print 'SUCCESS'


def new_stat_file(exp=curdir/'experiment'):
    exp = exp
    def next_id(exp=exp):
        return max(int(x.basename().split('result')[1][0]) for x in exp.listdir('result*.txt'))+1
    stat_file = exp/'result%d.txt'%next_id()
    return stat_file


###############################################################################
# Central works function
###############################################################################

count = 0
stat_file = new_stat_file()


def works(listofpackversions, stat_file=stat_file, env=env):
    global count
    count += 1
    config = listofpackversions
    #int2pkg = liquid.env.int2pkg
    #pkg2int = liquid.env.pkg2int

    #bidir = liquid.env.bidir_commits
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
        status = checkout(pkg, commit)
        t1 = clock()
        s = 'Install (%s,%s) in %f s\n'%(pkg, commit,(t1-t0).total_seconds())
        print s
        f.write(s)
        if status != 0:
            res = [False, 0, pkg2int[pkg], pkg2int['adel']]
            s = 'FAIL build %s\n'%pkg
            f.write(s)
            f.close()
            return res

    t2 = clock()
    status = run()
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
        res = [True, -1, -1]
        res = [True, 0, -1, -1]
    else:
        try:
            if liquidparser.knowcaller:
                res = [False, 0, pkg2int[status[1]], pkg2int[status[0]]]
            else:
                res = [False, 2, -1, -1]
        except:
            res = [False, 0, pkg2int['rpy2'], pkg2int['adel']]
    return res


###############################################################################
# Monkey patch liquidparser
###############################################################################

def monkey_patch(liquidparser, works, universe, knowcaller=knowcaller, env=env):
    liquidparser.works = works
    ordered_packages = universe

    sourcemap, default, todolist = liquid.variables_for_parser(ordered_packages, env=env)
    orderofpackages = [pkg2int[p] for p in ordered_packages]

    liquidparser.compatibilities = []
    liquidparser.orderofpackages = orderofpackages
    liquidparser.default = default
    liquidparser.sourcemap = sourcemap
    liquidparser.strongmemory = []
    constraints = {}
    liquidparser.todolist = todolist
    liquidparser.knowcaller = knowcaller

    return constraints, todolist


constraints, todolist = monkey_patch(liquidparser, works, universe, knowcaller, env)


###############################################################################
# Run the Horrible Thing (tm)
###############################################################################

f = open(stat_file, 'a')

f.write('knowcaller = %s\n'%(liquidparser.knowcaller))
f.write(str(pkgs)+('\n'*3))
f.close()

ti = clock()
try:
    endconfig = liquidparser.liquidclimber(constraints, todolist)
    print liquidparser.memory
    te = clock()
    s= "\nTotal number of tested configuration: %d \n"%(count)
    print s
    f = open(stat_file, 'a')
    f.write(s)
finally:
    restore()

res = []
for k, v in endconfig.iteritems():
    pkg = int2pkg[k]
    res.append('(%s,%s)'%(int2pkg[k], pkgs[int2pkg[k]][v-1]))

s = '\nEnd Configuration\n'
s+= '\n'.join(res)
print s
f.write(s)

s = '\n####################\n'
s+= 'Global time: %s\n'%(te-ti).total_seconds()
s+= '####################\n'
print s
f.write(s)
f.close()



"""