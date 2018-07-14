""" Test vclimb """

from __future__ import absolute_import

from os.path import exists
import versionclimber as vc
from versionclimber.config import load_config
from versionclimber.liquid import YAMLEnv
from versionclimber.algo import demandsupply
from versionclimber import version


def test_config():
    if exists('config.yaml'):
        config = load_config('config.yaml')
        packages = config['packages']
        return packages


def test_versions():
    versions = ("1.0.1 2.6.1 2.6.3 2.6.8 2.7.15 3.3.5").split()
    d = version.segment_versions(versions,'minor')
    assert(d.keys() == ['1.0', '2.6', '2.7', '3.3'])
    assert(d['2.6'] == ['2.6.1', '2.6.3', '2.6.8'])

