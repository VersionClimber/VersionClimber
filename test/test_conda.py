"""Test version recovery of Scikit.Learn and Scikit.Image on conda."""

from __future__ import absolute_import
from versionclimber import utils


def test_sklearn():
    versions = utils.conda_versions('scikit-learn')
    assert '0.20.0' in versions
    assert len(versions) >= 12


def test_skimage():
    versions = utils.conda_versions('scikit-image')
    assert '0.14.0' in versions
    assert len(versions) >= 7

def test_mtg_channels():
    versions = utils.conda_versions('openalea.mtg', channels=['openalea'])
    assert '2.0.1' in versions
    assert len(versions) >= 1

def test_nonpy():
    versions_default = utils.conda_versions('gmp')
    versions = utils.conda_versions('gmp', channels=['openalea'])
    if len(versions_default) < len(versions):
        assert len(versions_default) <= len(versions), str(len(versions_default)) + ', ' + str(len(versions))
        assert set(versions) - set(versions_default)
