"""
Climber complex tutorial

Package :
  - Alinea.Adel (svn)
Depends: 
  - Alinea.Caribu (svn)
  - OpenAlea.MTG
  - OpenAlea.PlantGL
Other depends:
  - pandas
  - rpy2, R
  - SciPy, NumPy, Matplotlib



1. Create a virtualenv

virtualenv --always-copy venv

2. Comment all PYTHONATH & PATH

3. Activate a virtualenv

source venv/bin/activate

4. Installation

pip install ipython==2.4

pip install --no-index -U ./pandas

pip install --no-index -U ./deploy
pip install --no-index -U ./sconsx
pip install --no-index -U ./openalea/grapheditor
pip install --no-index -U ./openalea/misc
pip install --no-index -U ./openalea/vpltk
pip install --no-index -U ./openalea/core
alea_install scons

pip install --no-index -U ./caribu
pip install --no-index -U --no-deps ./adel

pip install rpy2==38.1 to know available versions
pip install --no-index -U ./PlantGL
pip install --no-index -U ./newmtg



export DYLD_FALLBACK_LIBRARY_PATH=$VIRTUAL_ENV/lib/python2.7/site-packages/lib
export PYTHONPATH=/opt/local/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages
PATH="$VIRTUAL_ENV/lib/python2.7/site-packages/bin:$PATH"




Versions:

rpy2:
2.0.8, 2.1.0, 2.1.1, 2.1.2, 2.1.3, 2.1.4, 2.1.5, 2.1.6, 2.1.7, 2.1.8, 2.1.9, 2.2.0, 2.2.1, 2.2.2, 2.2.3, 2.2.4, 2.2.5, 2.2.6, 2.2.7, 2.3.0a1, 2.3.0b1, 2.3.0, 2.3.1, 2.3.2, 2.3.3, 2.3.4, 2.3.5, 2.3.6, 2.3.7, 2.3.8, 2.3.9, 2.3.10, 2.4.0, 2.4.1, 2.4.2, 2.4.3, 2.4.4, 2.5.0, 2.5.1, 2.5.2, 2.5.3, 2.5.4, 2.5.5, 2.5.6, 2.6.0, 2.6.1.dev0, 2.6.1, 2.6.2, 2.6.3, 2.7.0


newmtg
svn log | grep "^r[0-9]\+ | " | cut -d' ' -f1 | cut -c2- > revisions.csv

"""

from vflexql import liquid, liquidparser


###############################################################################

# MONKEY PATCHING

count = 0

def works(listofpackversions):
    """ Evaluation function that is run for each set of package version.

    This method is called by the liquid climber algorithm.
    """
    global count
    count += 1

    config = listofpackversions
    int2pkg = liquid.env.int2pkg
    pkg2int = liquid.env.pkg2int

    bidir = liquid.env.bidir_commits
    semantic_config = {}
    for pi, ci in config.iteritems():
        pkg = int2pkg[pi]
        commit = bidir[pkg][1][ci]
        semantic_config[pkg] = commit

    for pkg, commit in semantic_config.iteritems():
        liquid.checkout(pkg, commit)
        liquid.pip_install(pkg)

    status = liquid.run()

    if status == 0:
        res = [True, -1, -1]
        res = [True, 0, -1, -1]
    else:
        res = [False, pkg2int[status[1]], pkg2int[status[0]]]
        res = [False, 0, pkg2int[status[1]], pkg2int[status[0]]]
        #knowcaller=False
        res = [False, 2, pkg2int[status[1]], pkg2int[status[0]]]

    return res

liquidparser.works = works

###############################################################################


liquid.env.init(dir='/Users/pradal/devlp/project/vflexql/test/adel_pkgs',
                universe=('scikit-image', 'scikit-learn'))

liquid.activate()

ordered_packages = ('scikit-image', 'scikit-learn')
default = dict(zip(ordered_packages, ['v0.4', '0.8']))
sourcemap, default, todolist = liquid.variables_for_parser(ordered_packages, default=default)


_orderofpackages = ['scikit-image', 'scikit-learn']
orderofpackages = [liquid.env.pkg2int[p] for p in _orderofpackages]

compatibilities = []

#results, compatibilities = liquid.experiment()

# set global variables
liquidparser.compatibilities = compatibilities
liquidparser.orderofpackages = orderofpackages
liquidparser.default = default
liquidparser.sourcemap = sourcemap

constraints = {}

try:
    endconfig = liquidparser.liquidclimber(constraints, todolist)
    print liquidparser.memory
finally:
    liquid.restore_config()



"""
Initial config:

adel : 
MTG : 
pandas: 
caribu:
rpy2:   

# Complete test

import git
from vflexql import liquid, liquidparser
from vflexql.utils import sh, path

# Create a clean virtual environment

dir = path('/Users/pradal/devlp/project/vflexql/test/pkgs')
dir.chdir()

sh("virtualenv --always-copy venv_adel")

# activate Virtual Env
p = dir/'venv_adel/bin/activate_this.py'
execfile(p, dict(__file__=p))

# liquid

"""
"""
Initial config:

scikit-image : v0.4
scikit-learn : 0.8-branching

import git
from vflexql import liquid, liquidparser

liquid.env.init(dir='/Users/pradal/devlp/project/vflexql/test/pkgs',
                universe=('scikit-image', 'scikit-learn'), Tags=True)

commits = liquid.env.commits

liquid.env.commits = {p:[x for x in l if 'debian' not in str(x)] for p, l in commits.iteritems()}

p='pkgs/venv/bin/activate_this.py'
execfile(p, dict(__file__=p))

ordered_packages = ('scikit-image', 'scikit-learn')
default = dict(zip(ordered_packages, ['v0.4', '0.8']))
sourcemap, default, todolist = liquid.variables_for_parser(ordered_packages, default=default)

_orderofpackages = ['scikit-image', 'scikit-learn']
orderofpackages = [liquid.env.pkg2int[p] for p in _orderofpackages]

compatibilities = []

liquidparser.compatibilities = compatibilities
liquidparser.orderofpackages = orderofpackages
liquidparser.default = default
liquidparser.sourcemap = sourcemap

constraints = {}

endconfig = liquidparser.liquidclimber(constraints, todolist)

restore_config()



si_repo = git.Repo('pkgs/scikit-image/')
initial_si = si_repo.tags['v0.4'].commit

sl_repo = git.Repo('pkgs/scikit-learn/')
initial_sl = sl_repo.tags['0.8-branching'].commit

sl = liquid.env.commits['scikit-learn']
si = liquid.env.commits['scikit-image']

sl.index(initial_sl)
si.index(initial_si)


"""