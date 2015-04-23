"""
Simple demo
"""

from vflexql import liquid

liquid.init(dir='/Users/pradal/devlp/project/vflexql/test/simple',
     universe=('foo', 'goo', 'hoo'))

liquid.activate()

results = liquid.experiment()
print results

