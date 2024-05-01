""" Test vclimb """

from __future__ import absolute_import

from os.path import exists
import versionclimber as vc
from versionclimber.config import load_config
from versionclimber.liquid import YAMLEnv, pkg_versions
from versionclimber import version
from versionclimber.algo.demandsupply import findanchors
from versionclimber.utils import conda_full_depends
from versionclimber import reduceconfig




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


def my_reduce_config(config='config2.yaml'):
    packageversions, miniseries = my_segment_versions(config)
    anchors = findanchors(miniseries)
    universe = [l[0][0] for l in anchors]

    info_pkgs = {}
    for i, pkg in enumerate(universe):
        info = conda_full_depends(pkg)
        info_pkgs.update(info)

    pkg_versions = { l[0][0] : [version for name, version in l] for l in anchors}
    all_pairs = version.decimate_versions(pkg_versions, info_pkgs)

    # build a config to reduceconfig
    groups = version._build_config(all_pairs, universe)
    full_config = reduceconfig.reduce_config2(groups)

    configs = sort_pkgversions(full_config, universe)

    return configs


def sort_pkgversions(pkgversions, universe):
    confs = []

    for c in pkgversions:
        l = list(k.split('__') for k in c.split(' '))
        l = sorted(l, key=lambda pv:universe.index(pv[0]), reverse=True)
        
        #l = ' '.join('__'.join(pv) for pv in l)
        confs.append(l)

    confs = multisort(confs)

    return confs 

from versionclimber.utils import MyLooseVersion

def multisort(conf):
    c0 = conf[0]
    n = len(c0)

    for i in range(n):
        conf.sort(key=lambda conf: MyLooseVersion(conf[i][1]),
                  reverse=True)
    return conf

def test_sort():
    pkgvers = """
A2__4 P1__4 P3__6 P4__7 P6__1
A2__4 P1__4 P3__6 P4__7 P6__2
A2__4 P1__4 P3__19 P4__7 P6__1
A2__4 P1__4 P3__19 P4__7 P6__2
A2__4 P1__4 P3__6 P4__8 P6__1
A2__4 P1__4 P3__6 P4__8 P6__2
A2__4 P1__4 P3__19 P4__8 P6__1
A2__4 P1__4 P3__19 P4__8 P6__2
A2__4 P1__4 P3__6 P4__9 P6__1
A2__4 P1__4 P3__6 P4__9 P6__2
A2__4 P1__4 P3__19 P4__9 P6__1
A2__4 P1__4 P3__19 P4__9 P6__2
""".split('\n')
    pkgvers = list(filter(None, pkgvers))

    universe = 'P1 A2 P3 P4 P6'.split()
    universe.reverse()

    conf = sort_pkgversions(pkgvers, universe)

    conf_sorted = '\n'.join(' '.join(['__'.join(pv) for pv in c]) for c in conf)
    print(conf_sorted)
    return conf