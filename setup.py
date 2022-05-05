from setuptools import setup

# Packages list, namespace and root directory of packages

packages = ['versionclimber', 'versionclimber.algo']

# dependencies to other eggs
setup_requires = []
install_requires = []

name = 'VersionClimber'
description = 'Version Climber: System and Algorithms for Package evolution in Data Science.'
long_description = description

authors = 'Christophe Pradal, Sarah Cohen-Boulakia, Patrick Valduriez, Dennis Shasha'
authors_email = 'christophe.pradal@cirad.fr, shasha@courant.nyu.edu, Sarah.Cohen_Boulakia@lri.fr, Patrick.Valduriez@inria.fr'
url = 'https://github.com/VersionClimber/VersionClimber'
license = 'Cecill-C'

version='1.3.3'

setup(
    name=name,
    version=version,
    description=description,
    long_description=long_description,
    author=authors,
    author_email=authors_email,
    url=url,
    license=license,
    keywords='',

    # package installation
    packages=packages,

    zip_safe=False,

    # Dependencies
    entry_points={"console_scripts": ["vclimb = versionclimber.vclimb:main"]},
)
