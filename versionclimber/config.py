"""Read the configuration from yaml description file.

This module implements a Package object that can retrieve the versions and activate it at different versions.
"""

import yaml
import logging

from string import Template
import re

from versionclimber.utils import sh, pypi_versions, git_versions, svn_versions, conda_versions, Path

logger = logging.getLogger(__name__)

class Package(object):
    """Package description
    """

    def __init__(self,
                 name=None,
                 vcs='pypi',
                 url=None,
                 cmd='pip install -U',
                 version=None,
                 conda=False,
                 recipe=None,
                 conda_channels=None,
                 hierarchy='commit',
                 directory='.vclimb'):
        self.name = name
        self.vcs = vcs
        self.url = url
        self.cmd = cmd
        self.version = version
        self.hierarchy = hierarchy
        self.conda = bool(conda)
        self.dir = Path(directory).abspath()
        self.conda_channels = [] if not conda_channels else conda_channels
        if conda and recipe:
            self.recipe_dir = Path(recipe).abspath()
        else:
            self.recipe_dir = None

        if not self.dir.exists():
            self.dir.makedirs()

    def __str__(self):
        return self.name

    def clone(self):
        cwd = Path('.').abspath()

        if self.vcs == 'path':
            path_pkg = Path(self.url).abspath()

        pp = self.dir/self.name
        if pp.exists():
            logger.info('%s directory already exists. We use this version' % pp)
            pp.chdir()
            if self.vcs == 'git':
                cmd = 'git fetch -p'
                sh(cmd)
                cmd = 'git pull origin master'
            elif self.vcs == 'svn':
                cmd = 'svn update'
            elif self.vcs == 'path':
                (pp/'..').chdir()
                pp.rmtree()
            sh(cmd)
            cwd.chdir()

        elif self.vcs in ('pypi', 'conda'):
            pass
        elif self.vcs in ('git', 'svn'):
            if self.vcs == 'git':
                cmd = 'git clone %s %s' % (self.url, self.name)
            elif self.vcs == 'svn':
                cmd = 'svn checkout %s %s' % (self.url, self.name)

            self.dir.chdir()
            sh(cmd)
            cwd.chdir()

        if self.vcs == 'path':
            # copy tree url into pp
            path_pkg.copytree(pp)


    def versions(self, tags=True):
        pp = self.dir/self.name
        versions = []
        if self.vcs == 'pypi':
            versions = pypi_versions(self.name)
        elif self.vcs == 'conda':
            versions = conda_versions(self.name, channels= self.conda_channels)
        else:
            if not pp.exists():
                logger.info('We clone the package %s to get the versions'%self.name)
                self.clone()
            if self.vcs == 'git':
                versions = git_versions(pp, tags=tags)
            elif self.vcs == 'svn':
                versions = svn_versions(pp)
            elif self.vcs == 'path':
                versions = ['1.0']
            else:
                raise Exception('%s is not implemented yet'%self.vcs)

        # print '+++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
        # print 'VERSIONS (%s): '%(self.name), versions
        # print '+++++++++++++++++++++++++++++++++++++++++++++++++++++++++'

        return versions


    def checkout_update(self, commit, version=None):
        pp = self.dir/self.name
        cwd = Path('.').abspath()

        commit = str(commit)

        if not pp.exists():
            logger.warning('ERROR: %s has not been cloned (git) or checkout (svn).'%self.name)

        if self.vcs != 'path': # When package is under svn or git
            pp.chdir()

            if self.vcs == 'svn':
                update_cmd = 'svn update -r %s' % commit
            elif self.vcs == 'git':
                update_cmd = 'git checkout %s' % commit
            else:
                raise Exception('%s is not implemented yet' % self.vcs)

            logger.info('Checkout %s: %s'%(self.name, update_cmd))

            status = sh(update_cmd)

            cwd.chdir()

        if self.conda:
            if self.vcs == 'git' and commit=='master':
                return

            recipe_dir = self.recipe_dir
            conda_recipe_tpl = recipe_dir/'meta.yaml.tpl'

            _version = self.get_version(commit, version=version)

            src = open(conda_recipe_tpl).read()
            src = Template(src)
            src = src.substitute(dict(version=_version))

            conda_recipe = recipe_dir/'meta.yaml'

            f = open(conda_recipe, 'w')
            f.write(src)
            f.close()

            logger.info('Write %s from %s'%(conda_recipe, conda_recipe_tpl))

        return status


    def local_install(self, commit, version=None):
        """ Checkout or update the package to a given commit version.
        Install it with pip at this given revision.
        """
        channels = ' '.join(['-c '+ channel for channel in self.conda_channels])
        pkg_path = (self.dir / self.name).abspath()
        if self.vcs == 'pypi':
            cmd = '%s %s==%s' % (self.cmd, self.name, commit)
        elif self.vcs == 'conda':
            cmd_list = [self.cmd]
            cmd_list.append(channels)

            cmd_list.append('%s=%s' % (self.name, commit))

            cmd = ' '.join(cmd_list)

        else:
            self.checkout_update(commit, version=version)
            cmd = '%s %s' % (self.cmd, pkg_path)

            if self.conda:
                cmd = 'conda build %s %s'%(channels, self.recipe_dir)
                status = sh(cmd)
                if status:
                    return status

                _version = self.get_version(commit, version=version)
                cmd = 'conda install -y -f --no-deps --use-local %s=%s'%(self.name, _version)
        status = sh(cmd)
        return status


    def restore(self):
        """ Set the active commit version to HEAD or master. """
        if self.vcs == 'svn':
            self.checkout_update('HEAD')
        elif self.vcs == 'git':
            self.checkout_update('master')


    def get_version(self, commit, version=None):
        if (self.vcs == 'git') and (len(commit) == 40):
            return version
            # git commit that can not
        my_group = re.search(r'([\d.]+)', commit)
        if my_group:
            return my_group.group(1)
        else:
            return commit


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
