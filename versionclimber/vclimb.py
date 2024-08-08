"""Script to run versionclimber from a configuration file."""

from __future__ import absolute_import
from __future__ import print_function
import sys
import os
from optparse import OptionParser

from versionclimber import liquid
from versionclimber.algo import liquidparser, demandsupply
from versionclimber import server, client

def main():
    """This function is called by vclimb

    To obtain specific help, type::

        vclimb --help


    """

    usage = """
vclimb traverse the versions of the packages and get the optimal one.
Example

       vclimb server|client --conf config.yaml --log vclimb.log

vclimb can also print all the versions of the packages

        vclimb server|client --conf config.yaml  --version
"""

    parser = OptionParser(usage=usage)

    parser.add_option("--conf", dest='config', default='config.yaml',
        help="YAML configuration file")
    parser.add_option("--log", dest='log_file', default='versionclimber.log',
        help="Store logging information in this file")
    parser.add_option("-v", "--version", action="store_true", dest="version", default=False,
        help="Print versions of all packages")
    parser.add_option("-d", "--demandsupply", action="store_true", dest="demandsupply", default=True,
        help="Use the demand supply algorithm (default)")
    parser.add_option("-a", "--anchor", action="store_true", dest="anchor", default=False,
        help="Generate the cross-product of the anchor before testing all the configs.")
    parser.add_option("-r", "--reduce", action="store_true", dest="reduce", default=False,
        help="Query the channels to select only versions that are compatible to each others.")
    parser.add_option("-s", "--slaveid", dest="slaveid", default='0',
        help="Set the identifier of the client (client only) .")
    parser.add_option("--debug", action="store_true", dest="debug", default='True',
        help="Run the debug mode .")

    (opts, args)= parser.parse_args()

    mode_server = None
    if len(args) == 1:
        if args[0] not in ('client', 'server'):
            parser.error("argument must be client or server")
        else:
            mode_server = args[0]


    if (not opts.debug) and (opts.config == None):
        raise ValueError("""--conf must be provided. See help (--help)""")

    if opts.demandsupply:
        algo_module = demandsupply
    else:
        algo_module = liquidparser

    if not opts.version:
        algo_module.start_logging(opts.log_file)
        
    env = None
    if mode_server is None:
        env = liquid.YAMLEnv(opts.config, opts.demandsupply, opts.reduce)
    elif mode_server == 'server':
        env = server.ServerEnv(opts.config, demandsupply=opts.demandsupply, debug=opts.debug, reduce=opts.reduce)
    elif mode_server == 'client':
        env = client.ClientEnv(opts.config, demandsupply=opts.demandsupply, slaveid=opts.slaveid,
                               debug=opts.debug)

    if not opts.version:
        solutions = env.run(algo_module, opts.anchor)

        print(('\n' * 3))
        print('Solution is:')
        for sol in solutions:
            print(sol)
    else:
        env.print_versions(algo_module, opts.reduce)
