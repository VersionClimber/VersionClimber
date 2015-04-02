""" VFlexQL

Task 3: Report the version graph for each particular package
"""

import os
from utils import path, clone
import git

def versions(path):
    """

    """
    repo = git.Repo(path)
    print 'Branch : ', repo.active_branch.name

    commits = repo.iter_commits()

    for c in commits:
        print str(c), ' : ', c.summary, '(%d)'%c.authored_date
        yield c 

def tags(path):
    """

    """
    repo = git.Repo(path)

    l = [(t.commit.authored_date, t.name) for t in repo.tags]
    l.sort(key=lambda x: x[0], reverse=True)
    if l:
        res = zip(*l)[1]
        print res
    else:
        res = []
    return res


def test():
    pkgs = path('pkgs').abspath()
    

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

    print tags('pkgs/scikit-learn')