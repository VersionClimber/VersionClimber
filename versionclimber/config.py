"""
Read the configuration from yaml description file.

"""

import yaml
from path import path
from versionclimber.utils import sh

class Package(object):
    """Package description
    """

    def __init__(self,
                 name=None,
                 vcs='pypi',
                 url=None,
                 cmd='pip install -U',
                 version=None,
                 hierarchy='commit',
                 dir ='.'):
        self.name = name
        self.vcs = vcs
        self.url = url
        self.cmd = cmd
        self.version = version
        self.hierarchy = hierarchy
        self.dir = path('.').abspath()

    def __str__(self):
        return self.name

    def clone(self):
        cwd = path('.').abspath()
        pp = self.dir/self.name
        if pp.exists():
            print '%s directory already exists. We use this version' % pp
        elif self.vcs == 'pypi':
            pass
        else:
            if self.vcs == 'git':
                cmd = 'git clone %s %s' % (self.url, self.name)
            elif self.vcs == 'svn':
                cmd = 'svn checkout %s %s' % (self.url, self.name)

            self.dir.chdir()
            sh(cmd)
            cwd.chdir()




def load_config(yaml_filename):
    """ Create an environment from a yaml file.

    TODO: manage errors
    """
    f = open(yaml_filename)
    stream = f.read()

    data = yaml.load(stream)

    packages = []
    for pkg in data.get('packages', []):
        packages.append(Package(**pkg))

    run_cmd = data.get('run')
    return packages, run_cmd

#if __name__ == '__main__':
#    load_config('../examples/config.yaml')
