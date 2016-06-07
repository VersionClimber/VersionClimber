"""Script to run versionclimber from a configuration file."""

import sys
import os
from optparse import OptionParser

from versionclimber import liquid, liquidparser

def main():
    """This function is called by alea_create_package script that is installed
    on your system when installing OpenAlea.PkgBuilder package.

    To obtain specific help, type::

        alea_create_package --help


    """

    usage = """
vclimb traverse the versions of the packages and get the optimal one.
Example

       vclimb --config config.yaml --log vclimb.log
"""

    parser = OptionParser(usage=usage)

    parser.add_option("--conf", dest='config', default=None,
        help="YAML configuration file")
    parser.add_option("--log", dest='log_file', default='versionclimber.log',
        help="Store logging information in this file")

    (opts, args)= parser.parse_args()


    if opts.config == None:
        raise ValueError("""--conf must be provided. See help (--help)""")


    liquidparser.start_logging(opts.log_file)

    env = liquid.YAMLEnv(opts.config)
    solutions = env.run(liquidparser)

    print('\n' * 3)
    print('Solution is:')
    for sol in solutions:
        print(sol)

