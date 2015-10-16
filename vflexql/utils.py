""" git utils

"""

import os
from path import path
import subprocess
import re
import json
import urllib2
from distutils.version import LooseVersion


def sh(cmd):
    print cmd
    return os.system(cmd)


def clone(repo, pkg):
    cmd = 'git clone https://github.com/%s/%s' % (repo, pkg)
    sh(cmd)


def pypi_versions(package_name):
    """ Retrieve the different versions of a package on PyPi.

    Return the sorted list.
    """
    url = "https://pypi.python.org/pypi/%s/json" % (package_name,)
    data = json.load(urllib2.urlopen(urllib2.Request(url)))
    versions = data["releases"].keys()
    versions.sort(key=LooseVersion)
    # print versions
    return versions


def git_versions(package_path, tags=False):
    """ Return a list of git versions of a package.
    """
    from vflexql import multigit
    if tags:
        return list(multigit.tags(package_path))
    else:
        return list(multigit.versions(package_path))


def svn_versions(package_path):
    """ Return the svn versions """
    cwd = path('.').abspath()
    pp = path(package_path)
    if pp.exists():
        pp.chdir()
    else:
        return []

    revisions = []
    try:
        svn_revs = subprocess.check_output(['/opt/local/bin/svn', 'log'])
        revisions = [l.split(' | ')[0] for l in re.split("\n+", svn_revs)
                     if re.match(r"^r[0-9]+", l)]
        revisions.reverse()
    except:
        pass
    cwd.chdir()

    return revisions
