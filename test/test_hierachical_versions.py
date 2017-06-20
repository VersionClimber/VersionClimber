""" Test version recovery of Scikit.Learn and Scikit.Image """

from versionclimber import utils, version


def test_sklearn():
    versions = utils.pypi_versions('scikit-learn')
    majors = version.majors(versions)
    minors = version.minors(versions)
    patchs = version.patchs(versions)

    assert len(majors) >= 1
    assert len(minors) >= 14
    assert len(patchs) >= 24

    assert len(majors) <= len(minors) <= len(patchs) <= len(versions)



def test_skimage():
    versions = utils.pypi_versions('scikit-image')
    assert versions[0] == '0.7.2'

    majors = version.majors(versions)
    minors = version.minors(versions)
    patchs = version.patchs(versions)

    assert len(majors) >= 1
    assert len(minors) >= 7
    assert len(patchs) >= 18

    assert len(majors) <= len(minors) <= len(patchs) <= len(versions)
