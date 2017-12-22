"""
Simple test to check the different imports

"""
from __future__ import absolute_import
def test1():
    """ Test simple import """
    import versionclimber

def test2():
    import versionclimber.utils
    import versionclimber.liquid
    import versionclimber.config
    import versionclimber.version


def test3():
    import versionclimber.liquidparser
    import versionclimber.liquidparser_pessimistic

def test4():
    import versionclimber.vclimb

