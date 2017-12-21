""" VFlexQL

Task 3: Report the version graph for each particular package
"""

from __future__ import absolute_import
from __future__ import print_function
import os
import git
try:
    from path import Path
except ImportError:
    from path import path as Path


def versions(path):
    """

    """
    repo = git.Repo(path)
    """
    try:
        print 'Branch : ', repo.active_branch.name
    except:
        pass
    commits = repo.iter_commits()

    for c in commits:
        print c.name_rev, ' : ', c.summary, '(%d)'%c.authored_date
        yield c
    """
    l = [(c.authored_date, str(c)) for c in repo.iter_commits()]
    l.sort(key=lambda x: x[0])
    if l:
        res = zip(*l)[1]
        print(res)
    else:
        res = []
    return res

def tags(path):
    """

    """
    repo = git.Repo(path)

    l = [(t.commit.authored_date, t.name) for t in repo.tags]
    l.sort(key=lambda x: x[0])
    if l:
        res = zip(*l)[1]
        print(res)
    else:
        res = []
    return res


def test():
    from versionclimber.utils import path, clone

    pkgs = Path('pkgs').abspath()


    sklearn = ('scikit-learn', 'scikit-learn')
    openalea = ('openalea', 'openalea')

    if not (pkgs/sklearn[-1]).isdir():
        pkgs.cd()
        clone(*sklearn)
        (pkgs/'..').cd()

    if not (pkgs/openalea[-1]).isdir():
        pkgs.cd()
        clone(*openalea)
        (pkgs/'..').cd()

    _tags = tags('pkgs/scikit-learn')
    print(_tags)

    _versions = list(versions('pkgs/scikit-learn'))
    return _tags, _versions

def universe_versions(dir='simple', universe=('foo', 'goo', 'hoo'), Tags=False):
    pkgs = Path(dir).abspath()

    res = {}
    for pkg in universe:
        if not Tags:
            l = list(versions(dir+'/'+pkg))
        else:
            l = list(tags(dir+'/'+pkg))
        res[pkg] = l

    return res

def branch_names(dir='simple', universe=('foo', 'goo', 'hoo')):
    _dir = Path(dir)

    res = {}
    for pkg in universe:
        p = _dir/pkg
        repo = git.Repo(p)
        res[pkg] = repo.active_branch.name

    return res
