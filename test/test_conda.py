"""Test version recovery of Scikit.Learn and Scikit.Image on conda."""

from __future__ import absolute_import
from versionclimber import utils


def test_sklearn():
    versions = utils.conda_versions('scikit-learn', build='')
    assert ('0.19.0' in versions)
    assert len(versions) >= 20


def test_skimage():
    versions = utils.conda_versions('scikit-image', build='')
    assert ('0.13.0' in versions)
    assert len(versions) >= 13

def test_mtg_channels():
    versions = utils.conda_versions('openalea.mtg', channels=['openalea3'], build='')
    assert '2.1.1' in versions
    assert len(versions) >= 1

def test_nonpy():
    versions_default = utils.conda_versions('gmp', build='')
    versions = utils.conda_versions('gmp', channels=['openalea'], build='')
    if len(versions_default) < len(versions):
        assert len(versions_default) <= len(versions), str(len(versions_default)) + ', ' + str(len(versions))
        assert set(versions) - set(versions_default)
