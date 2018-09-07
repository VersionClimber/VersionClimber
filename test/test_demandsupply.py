""" Test vclimb """

from __future__ import absolute_import

from os.path import exists
import versionclimber as vc
from versionclimber.config import load_config
from versionclimber.liquid import YAMLEnv, pkg_versions
from versionclimber.algo import demandsupply
from versionclimber import version


def test_config():
    if exists('config.yaml'):
        config = load_config('config.yaml')
        packages = config['packages']
        return packages


def test_versions():
    versions = ("1.0.1 2.6.1 2.6.3 2.6.8 2.7.15 3.3.5").split()
    d = version.segment_versions(versions,'minor')
    assert(set(d.keys()) >= set(['1.0', '2.6', '2.7', '3.3']))
    assert(set(d['2.6']) >= set(['2.6.1', '2.6.3', '2.6.8']))


def my_segment_versions(config='config.yaml'):
    config = load_config(config)
    pkgs = config['packages']
    universe = [pkg.name for pkg in pkgs]

    init_config = { pkg.name: (pkg.version, pkg.hierarchy) for pkg in pkgs}

    _pkg_versions = {}
    for pkg in pkgs:
        tags = pkg.hierarchy != 'commit'
        vers = pkg.versions(tags=tags)
        _pkg_versions[pkg.name] = vers

    # retrieve for each package (e.g. numpy, scipy, ...) the set of versions
    commits = pkg_versions(universe, init_config, _pkg_versions, {})


    packageversions = [[[pkg, c] for c in commits[pkg]] for pkg in universe]

    # TODO : to improve in a more generic way
    miniseries = []
    for pkg in universe:
        versions = commits[pkg]
        # parametrise the extraction type for each package (major, minor, patch, commit)
        v_dict = version.segment_versions(versions, type='minor')
        for _version in v_dict:
            miniseries.append([pkg, 'supply-constant', v_dict[_version]])


    return packageversions, miniseries
