"""Test version recovery of Scikit.Learn and Scikit.Image on conda."""

from __future__ import absolute_import
from versionclimber import utils


def test_sklearn():
    versions = utils.conda_versions('scikit-learn')
    assert versions[0] == '0.11'
    assert len(versions) >= 16


def test_skimage():
    versions = utils.conda_versions('scikit-image')
    assert versions[0] == '0.7.2'
    assert len(versions) >= 12

def test_mtg_channels():
    versions = utils.conda_versions('openalea.mtg', channels=['openalea'])
    assert versions[0] == '2.0.0'
    assert len(versions) >= 1

def test_nonpy():
    versions_default = utils.conda_versions('gmp')
    versions = utils.conda_versions('gmp', channels=['openalea'])

    assert len(versions_default) < len(versions)
    assert set(versions) - set(versions_default)
