""" Test vclimb """

from __future__ import absolute_import
import versionclimber as vc
from versionclimber.config import load_config
from versionclimber.liquid import YAMLEnv
from versionclimber import liquidparser


def test_vclimb():
    status = vc.utils.sh('vclimb -h')
    assert(status == 0)


def test_config():
    config = load_config('config.yaml')
    assert len(config['packages']) == 2


def test_run_config():
    env = YAMLEnv('config.yaml')

    #solutions = env.run(liquidparser)
    #assert len(solutions) == 2

