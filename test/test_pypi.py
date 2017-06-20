""" Test version recovery of Scikit.Learn and Scikit.Image """

from versionclimber import utils


def test_sklearn():
    versions = utils.pypi_versions('scikit-learn')
    assert versions[0] == '0.9'
    assert len(versions) >= 24



def test_skimage():
    versions = utils.pypi_versions('scikit-image')
    assert versions[0] == '0.7.2'
    assert len(versions) >= 18
