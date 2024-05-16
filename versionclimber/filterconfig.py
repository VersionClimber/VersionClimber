from .algo.demandsupply import findanchors
from .utils import conda_full_depends
from . import version
from . import reduceconfig


def filter_config(miniseries):
    """Return a reduce configuration by applying a set of constraints associated with each package and version"""
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

    configs = version.sort_pkgversions(full_config, universe)

    return configs
