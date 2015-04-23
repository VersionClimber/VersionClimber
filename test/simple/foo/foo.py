""" Test module for liquid VM

Three packages: foo, goo and hoo
The call graph is : hoo -> goo -> foo -> hoo

"""

import hoo


def foo(b=2):
    """ call hoo.f """
    a = hoo.f(b)
    print a
    return a
