import versionclimber
from versionclimber import liquid
from versionclimber import liquidparser

###############################################################################
# Load config

config_file = 'config.yaml'
env = liquid.YAMLEnv(config_file)
solutions = env.run(liquidparser)

print('Solution is: \n%s\n'%('\n'.join(solutions)))
