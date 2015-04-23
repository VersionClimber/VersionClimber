""" Test module for liquid VM

Three packages: foo, goo and hoo
The call graph is : hoo -> goo -> foo -> hoo

"""

import goo


def hoo():
    """ call goo """
    a = goo.goo()
    return a


def f(*args, **kwds):
    s = "called by foo " + ' '.join(map(str,args))
    return s
