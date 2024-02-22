""" Test version recovery of Scikit.Learn and Scikit.Image """

from __future__ import absolute_import
from versionclimber.conda_version import VersionSpec


def test_versions():
    versions = [
        '0.17.1',
        '0.18.0',
        '0.18.1',
        '0.19.0',
        '0.19.1',
        '1.0.0',
        '1.0.1',
        '1.1.0',
        '1.2.0',
        '1.2.1']
    spec = VersionSpec('>0.19,<=1.1')
    match_versions = [v for v in versions if spec.match(v)] 
    assert match_versions == ['0.19.1', '1.0.0', '1.0.1', '1.1.0']
