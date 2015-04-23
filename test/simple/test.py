import sys, traceback
try:
    import foo
    from hoo import hoo

    hoo()
except Exception, e:
    f = open('error.txt','w')
    traceback.print_exc(file=f)
    f.close()
    raise e

