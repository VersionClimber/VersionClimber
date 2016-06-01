import git
import versionclimber
from versionclimber import liquid, config
from versionclimber import liquidparser
###############################################################################
# Load config

config_file = 'config.yaml'
env = liquid.YAMLEnv(config_file)

constraints, todolist = env.monkey_patch(liquidparser)

try:
    endconfig = liquidparser.liquidclimber(constraints, todolist)
    print liquidparser.memory
finally:
    env.restore()
