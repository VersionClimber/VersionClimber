from versionclimber import liquid, config

###############################################################################
# Load config

config_file = 'config.yaml'

pkgs, cmds = config.load_config(config_file)
print("pkgs in config:\n", ["  " + str(pkg) + "\n" for pkg in pkgs])
print("testing commands:\n", ["  " + str(cmd) + "\n" for cmd in cmds])

###############################################################################
# Create a Virtual Env

pkg_versions = {}
for pkg in pkgs:
    print('Get %s' % pkg)
    pkg.clone()
    vers = pkg.versions(tags=False)
    print("Available version: ", vers)
    pkg_versions[pkg.name] = vers

universe = [pkg.name for pkg in pkgs]
init_config = {}
for pkg in pkgs:
    init_config[pkg.name] = (pkg.version, pkg.hierarchy)

# retrieve for each package (e.g. numpy, scipy, ...) the set of versions
_pkgs = liquid.pkg_versions(universe, init_config, pkg_versions, {})
env = liquid.MyEnv(universe, _pkgs)
