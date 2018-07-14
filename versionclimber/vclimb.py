"""Script to run versionclimber from a configuration file."""

from __future__ import absolute_import
from __future__ import print_function
import sys
import os
from optparse import OptionParser

from versionclimber import liquid
from versionclimber.algo import liquidparser, demandsupply

# Do we need a specific option to decide if we run the new algorithm?
DEMANDSUPPLY = True

if DEMANDSUPPLY:
    algo_module = demandsupply
else:
    algo_module = liquidparser

def main():
    """This function is called by vclimb

    To obtain specific help, type::

        vclimb --help


    """

    usage = """
vclimb traverse the versions of the packages and get the optimal one.
Example

       vclimb --conf config.yaml --log vclimb.log

vclimb can also print all the versions of the packages

        vclimb --conf config.yaml  --version
"""

    parser = OptionParser(usage=usage)

    parser.add_option("--conf", dest='config', default='config.yaml',
        help="YAML configuration file")
    parser.add_option("--log", dest='log_file', default='versionclimber.log',
        help="Store logging information in this file")
    parser.add_option("-v", "--version", action="store_true", dest="version", default=False,
        help="Print versions of all packages")

    (opts, args)= parser.parse_args()


    if opts.config == None:
        raise ValueError("""--conf must be provided. See help (--help)""")

    if not opts.version:
        algo_module.start_logging(opts.log_file)

    env = liquid.YAMLEnv(opts.config)

    print('version ', opts.version)


    if not opts.version:
        solutions = env.run(algo_module)

        print(('\n' * 3))
        print('Solution is:')
        for sol in solutions:
            print(sol)
    else:
        env.print_versions()
