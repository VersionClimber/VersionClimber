""" Version utilities

"""
from __future__ import absolute_import
from collections import OrderedDict
from six.moves import range
from six.moves import zip

from .conda_version import VersionSpec

# Select major, minor, patch and commit versions
def _major(version):
    return version.split('.')[0]


def _minor(version):
    return '.'.join(version.split('.')[:2])


def _patch(version):
    return '.'.join(version.split('.')[:3])


def _version(version, digit=-1):
    if len(version) < 4:
        version = '%4s' % version
        version = version.replace(' ', '0')
    return version[:digit]


def hversions(seq, type='major'):
    """ Returns a list of versions selected depending on its types (major, minor, patch)
    """
    _versions = {}
    _result = []

    if '.' in seq[0]:
        f = _major if type == 'major' else _minor if type == 'minor' else _patch
        for v in reversed(seq):
            ver = f(v)
            if ver not in _versions:
                _versions[ver] = v
                _result.append(v)
    else:
        digit = -3 if type == 'major' else -2 if type == 'minor' else -1
        f = _version
        for v in reversed(seq):
            ver = f(v, digit)
            if ver not in _versions:
                _versions[ver] = v
                _result.append(v)

    _result = list(reversed(_result))
    # print '+++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
    # print 'HIERARCHICAL VERSIONS: ', _result
    # print '+++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
    return _result


def hierarchical_versions(seq, type='major'):
    """ Returns a list of versions selected depending on its types (major, minor, patch)
    """
    _versions = OrderedDict()

    if '.' in seq[0]:
        f = _major if type == 'major' else _minor if type == 'minor' else _patch
        for v in reversed(seq):
            ver = f(v)
            if ver not in _versions:
                _versions[ver] = v

    else:
        digit = -3 if type == 'major' else -2 if type == 'minor' else -1
        f = _version
        for v in reversed(seq):
            ver = f(v, digit)
            if ver not in _versions:
                _versions[ver] = v

    return OrderedDict(list(reversed(list(zip(list(_versions.keys()),
                                              list(_versions.values()))))))

def segment_versions(seq, type='major'):
    """ Create mini-series of versions between major, minor and patch.
    return a list of list.

    :Parameter: type = major, minor, patch
    """
    _versions = OrderedDict()

    if '.' in seq[0]:
        f = _major if type == 'major' else _minor if type == 'minor' else _patch
        for v in seq:
            ver = f(v)
            _versions.setdefault(ver, []).append(v)

    else:
        digit = -3 if type == 'major' else -2 if type == 'minor' else -1
        f = _version
        for v in seq:
            ver = f(v, digit)
            _versions.setdefault(ver, []).append(v)

    return OrderedDict(zip(_versions.keys(),
                           _versions.values()))



def majors(seq):
    return hversions(seq, type='major')


def minors(seq):
    return hversions(seq, type='minor')


def patchs(seq):
    return hversions(seq, type='patch')


def take(seq, p):
    """ Takes p values in a sequence seq.
    With the first and last value.
    """
    n = len(seq)
    step = n / (p - 1)
    values = [seq[0]]
    indices = list(range(step, n - step + 1, step))[-p + 2:]
    values.extend([seq[i] for i in indices])
    if values[-1] != seq[-1]:
        values.append(seq[-1])

    return values

def decimate_versions(pkg_versions, info_pkgs):
    """ return a dict of package : dict(package: dict(package : [version]) 
    """
    result = dict()
    pkg_names = list(pkg_versions)

    def get_deps(pkg):
        deps = [d for d in pkg['depends'] for name in pkg_names if (name+' ') in d]
        res = {dep.split()[0]:dep.split()[1] for dep in deps}
        return res

    for pkg in pkg_names:

        result[pkg] = dict()
        versions = pkg_versions[pkg]

        for p in info_pkgs[pkg]:
            # Check if the version is in the pkg_versions
            v = p['version']
            if v not in versions:
                continue
            # check dependencies
            pkg_version_dep = result[pkg].setdefault(v, [])
            new_pkg_version = dict()
            deps = get_deps(p)
            if deps:
                add_it = True
                for pn in deps:
                    constraint = VersionSpec(deps[pn])
                    match_versions = [v for v in pkg_versions[pn] if constraint.match(v)] 
                    if not match_versions:
                        add_it = False
                        break
                    new_pkg_version[pn] = match_versions
                if add_it and (new_pkg_version not in pkg_version_dep):
                    pkg_version_dep.append(new_pkg_version)
            if not result[pkg][v]:
                del  result[pkg][v]
            

    return result


def _get_one_config(package, v, dep, pkg_order):
    l = []
    l.append(package+'__'+v)
    for p in pkg_order:
        if p not in dep:
            continue  
        sub_config = ' '.join([(p+'__'+vp) for vp in dep[p]])
        if len(dep[p]) > 1:
            l.append('['+sub_config+']')
        else:
            l.append(sub_config)

    return ' '.join(l)


def _build_config(all_pairs: dict, universe: list):
    """
    Transform all_pairs into a group of str 

    Parameters:
        - all_pairs : dict of dict
            for each package , a dict of versions with its dependencies.
    
    Example:
        all_pairs = {'numpy': {'1.9.3': [{'python': ['3.7.0']}]}
    """

    large_config = []
    config = list(all_pairs)
    # we traverse all the config
    # package is a string, version also
    for package in config:
        _config = []
        for v in all_pairs[package]:
            for dep in all_pairs[package][v]:
                if not dep:
                    continue
                l = _get_one_config(package, v, dep, universe)
                _config.append(l)

        _config = list(set(_config))
        if _config:
            print(_config)
            large_config.append(_config)
            print()



    #print('\n'.join(large_config))
    #print('#lines : ', len(large_config))
    return large_config

def write_config(large_config: list, filename : str):
    groups = []
    for g in large_config:
        groups.append('\n'.join(g))
        groups.append('')

    f = open(filename, 'w')
    f.write('\n'.join(groups))
    f.close()

