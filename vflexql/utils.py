""" git utils

"""

import os
from path import path


def sh(cmd):
    print cmd
    return os.system(cmd)


def clone(repo, pkg):
    cmd = 'git clone https://github.com/%s/%s' % (repo, pkg)
    sh(cmd)
