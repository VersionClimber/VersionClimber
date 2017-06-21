""" git utils

"""

import os
try:
    from path import Path
except ImportError:
    from path import path as Path

import subprocess
from subprocess import Popen, PIPE
import re
import json
import urllib2
import datetime
import logging
from distutils.version import LooseVersion
import multigit

logger = logging.getLogger(__name__)

def clock():
    """ Return the actual date. """
    return datetime.datetime.now()


def sh(cmd):
    logger.info(cmd)
    return os.system(cmd)


def new_stat_file(exp='experiment'):
    exp = Path(exp)
    def next_id(exp=exp):
        l = [int(x.basename().split('result')[1][0]) for x in exp.listdir('result*.txt')]
        n = max(l)+1 if l else 1
        return n
    stat_file = exp/'result%d.txt'%next_id()
    return stat_file

def clone(repo, pkg):
    cmd = 'git clone https://github.com/%s/%s' % (repo, pkg)
    sh(cmd)


def pypi_versions(package_name):
    """ Retrieve the different versions of a package on PyPi.

    Returns the versions as a sorted list.
    """
    url = "https://pypi.python.org/pypi/%s/json" % (package_name,)
    data = json.load(urllib2.urlopen(urllib2.Request(url)))
    versions = data["releases"].keys()
    versions.sort(key=LooseVersion)

    return versions

def conda_versions(package_name, channels=[], build='py27'):
    """ Retrieve the different versions of a package on anaconda.

    Returns the versions as a sorted list.
    """
    cmd = 'conda search -f %s --json'%(package_name,)
    cmd_list = cmd.split()

    for channel in channels:
        cmd_list.append('-c')
        cmd_list.append(channel)

    json_data = call_and_parse(cmd_list)
    if package_name not in json_data:
        return []

    pkgs = json_data[package_name]

    versions = [d['version'] for d in pkgs if ('py' not in d['build']) or (build in d['build'])]
    versions = list(set(versions))
    versions.sort(key=LooseVersion)

    return versions


def git_versions(package_path, tags=False):
    """ Return a list of git versions of a package.


    """
    if tags:
        return list(multigit.tags(package_path))
    else:
        return list(multigit.versions(package_path))


def svn_versions(package_path):
    """ Extract all the svn versions of a given directory

    """
    cwd = Path('.').abspath()
    pp = Path(package_path)
    if pp.exists():
        pp.chdir()
    else:
        return []

    revisions = []
    try:
        svn_revs = subprocess.check_output(['svn', 'log'])
        revisions = [l.split(' | ')[0] for l in re.split("\n+", svn_revs)
                     if re.match(r"^r[0-9]+", l)]
        revisions.reverse()
    except:
        pass
    cwd.chdir()

    return revisions

def call_and_parse(cmd_list):
    p = Popen(cmd_list, stdout=PIPE, stderr=PIPE)
    stdout, stderr = p.communicate()
    if stderr.decode().strip():
        raise Exception('conda %r:\nSTDERR:\n%s\nEND' % (cmd_list,
                                                         stderr.decode()))
    return json.loads(stdout.decode())
