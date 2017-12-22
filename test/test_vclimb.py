""" Test vclimb """

from __future__ import absolute_import

from os.path import exists
import versionclimber as vc
from versionclimber.config import load_config
from versionclimber.liquid import YAMLEnv
from versionclimber import liquidparser


def test_vclimb():
    status = vc.utils.sh('vclimb -h')
    assert(status == 0)


def test_config():
    if exists('config.yaml'):
        config = load_config('config.yaml')
        assert len(config['packages']) == 2


def test_run_config():
    if exists('config.yaml'):
        env = YAMLEnv('config.yaml')

        # too long to run in test
        #solutions = env.run(liquidparser)
        #assert len(solutions) == 2

