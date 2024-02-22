""" Test version recovery of Scikit.Learn and Scikit.Image """

from __future__ import absolute_import
from versionclimber import utils, version
from versionclimber.conda_version import VersionSpec
import reduceconfig

def test_numpy_scipy():
    python_versions = utils.conda_versions('python', channels=['conda-forge'], build='')
    numpy_versions = utils.conda_versions('numpy', channels=['conda-forge'], build='')
    scipy_versions = utils.conda_versions('scipy', channels=['conda-forge'], build='')
    # Implement smth like semver3 to see if a version match with constraints

    # Algo : search who depends on python
    # scipy -> (python, numpy), numpy -> python
    cmd = "conda search numpy -c conda-forge -C --info --json"
    cmd_list = cmd.split()
    json_data = utils.call_and_parse(cmd_list)

    # Todo

    # 0. get all the packages/versions
    # 1. add a method to util to retrieve constraints
    # 2. make a request to retrive all the versions in one shot
    # 3. traverse for each version all the packages deps and retrieve the versions
    # 4. parsing des contraintes
    # 5. appelle reduce config

def test_skimage():
    versions = utils.pypi_versions('scikit-image')
    assert versions[0] == '0.7.2'

    majors = version.majors(versions)
    minors = version.minors(versions)
    patchs = version.patchs(versions)

    assert len(majors) >= 1
    assert len(minors) >= 7
    assert len(patchs) >= 18

    assert len(majors) <= len(minors) <= len(patchs) <= len(versions)

def depends(pkg, deps=None):
    """return all the versions of a package with specifications"""
    cmd = "conda search %s -c conda-forge -C --info --json"%(pkg)
    cmd_list = cmd.split()
    json_data = utils.call_and_parse(cmd_list)
    return json_data

def build_versions(versions):
    packages = list(versions.keys())


def test_decimate_version():
    config = ['python', 'numpy', 'scipy']
    pkg_versions = { pkg: 
                    utils.conda_versions(pkg, 
                                         channels=['conda-forge'], build='') 
                        for pkg in config}

    info_pkgs = {}
    for i, pkg in enumerate(config):
        info = depends(pkg, config[:i]+config[i+1:])
        info_pkgs.update(info)

    all_pairs = decimate(pkg_versions, info_pkgs)

    large_config = get_config(all_pairs=all_pairs)

    write_config(large_config, "toto.txt")

    return reduceconfig.reduce_config(large_config)


def decimate(pkg_versions, info_pkgs):
    """ return a dict of package : dict(version: dict(package : [version]) 
    """
    result = dict()
    pkg_names = list(pkg_versions)

    def get_deps(pkg):
        deps = [d for d in pkg['depends'] for name in pkg_names if (name+' ') in d]
        res = {dep.split()[0]:dep.split()[1] for dep in deps}
        return res

    for pkg in pkg_names:
        versions = set(pkg_versions[pkg])
        result[pkg] = dict()
        for p in info_pkgs[pkg]:
            # Check if the version is in the pkg_versions
            v = p['version']
            if v not in versions:
                continue
            # check dependencies
            pkg_version_dep = result[pkg].setdefault(v, [])
            new_pkg_version = dict()
            pkg_version_dep.append(new_pkg_version)
            deps = get_deps(p)
            if deps:
                for pn in deps:
                    constraint = VersionSpec(deps[pn])
                    match_versions = [v for v in pkg_versions[pn] if constraint.match(v)] 
                    new_pkg_version[pn] = match_versions

    print(result)
    return result

    
    
    # get version for each package : info_pkgs[i]['version'] 

    # -> use one class of conda_version
    # Check if it is in pkg_versions
    # -> use one class of conda_version 

    # get the deps : info_pkgs[i]['depend']
    # -> [dep for dep in depends if pkg_name in dep]

    # get the version constraint
    # [d.split() for d in depends]

    # filter the versions

def get_one_config(package, v, dep):
    l = []
    l.append(package+'__'+v)
    for p in dep:  
        sub_config = ' '.join([(p+'__'+vp) for vp in dep[p]])
        l.append('['+sub_config+']')

    return ' '.join(l)

def get_config(all_pairs):
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
                #print(dep)
                l = get_one_config(package, v, dep)
                _config.append(l)
        large_config.append('')
        _config = list(set(_config))
        large_config.extend(_config)

    print('\n'.join(large_config))
    print('#lines : ', len(large_config))
    return large_config

def write_config(large_config: list, filename : str):
    f = open(filename, 'w')
    f.write('\n'.join(large_config))
    f.close()