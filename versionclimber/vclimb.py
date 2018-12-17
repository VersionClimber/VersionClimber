"""Script to run versionclimber from a configuration file."""

from __future__ import absolute_import
from __future__ import print_function
import sys
import os
from optparse import OptionParser

from versionclimber import liquid
from versionclimber.algo import liquidparser, demandsupply, demandsupply_optimistic


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
    parser.add_option("-d", "--demandsupply", action="store_true", dest="demandsupply", default=True,
        help="Use the demand supply algorithm")
    parser.add_option("-a", "--anchor", action="store_true", dest="anchor", default=False,
        help="Generate the cross-product of the anchor before testing all the configs.")

    (opts, args)= parser.parse_args()


    if opts.config == None:
        raise ValueError("""--conf must be provided. See help (--help)""")

    if opts.demandsupply:
        algo_module = demandsupply_optimistic
    else:
        algo_module = liquidparser

    if not opts.version:
        algo_module.start_logging(opts.log_file)

    env = liquid.YAMLEnv(opts.config, opts.demandsupply)

    print('version ', opts.version)


    if not opts.version:
        solutions = env.run(algo_module, opts.anchor)

        print(('\n' * 3))
        print('Solution is:')
        for sol in solutions:
            print(sol)
    else:
        env.print_versions()
