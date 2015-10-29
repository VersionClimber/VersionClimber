""" Test module for liquid VM

Three packages: foo, goo and hoo
The call graph is : hoo -> goo -> foo -> hoo

"""

import foo


def goo():
    """ call foo """
    a = foo.foo(b=1)
    return a
