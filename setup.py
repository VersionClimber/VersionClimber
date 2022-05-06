from setuptools import setup, find_packages

# Packages list, namespace and root directory of packages

packages = find_packages('.')

name = 'VersionClimber'
description = 'Version Climber: System and Algorithms for Package evolution in Data Science.'
long_description = description

authors = 'Christophe Pradal, Sarah Cohen-Boulakia, Patrick Valduriez, Dennis Shasha'
authors_email = 'christophe.pradal at cirad.fr, shasha at courant.nyu.edu, Sarah.Cohen_Boulakia at lri.fr, Patrick.Valduriez at inria.fr'
url = 'https://github.com/VersionClimber/VersionClimber'
license = 'Cecill-C'

version='1.3.4'

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

    packages=packages,
    zip_safe=False,

    # Dependencies
    entry_points={"console_scripts": ["vclimb = versionclimber.vclimb:main"]},
)
