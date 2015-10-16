# -*- coding: utf-8 -*-
__revision__ = "$Id: $"

from setuptools import setup, find_packages

# Packages list, namespace and root directory of packages

packages = ['vflexql']

# dependencies to other eggs
setup_requires = []
install_requires = []

# web sites where to find eggs
dependency_links = ['http://openalea.gforge.inria.fr/pi']

name = 'VFlexQL'
description = 'VFlexQL : Version Flexible Query Language'
long_description = '''

'''
authors = 'Christophe Pradal, Sarah Cohen-Boulakia, Patrick Valduriez, Dennis Shasha'
authors_email = 'christophe.pradal@inria.fr shasha@courant.nyu.edu Sarah.Cohen_Boulakia@lri.fr Patrick.Valduriez@inria.fr'.split()
url = 'http://openalea.gforge.inria.fr'
license = 'Cecill-C'

setup(
    name=name,
    version='1.0.0',
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
    setup_requires=setup_requires,
    install_requires=install_requires,
    dependency_links=dependency_links,
    )
