""" Version utilities

"""
from collections import OrderedDict


# Select major, minor, patch and commit versions
def _major(version):
    return version.split('.')[0]


def _minor(version):
    return '.'.join(version.split('.')[:2])


def _patch(version):
    return '.'.join(version.split('.')[:3])


def _version(version, digit=-1):
    if len(version) < 4:
        version = '%4s' % version
        version = version.replace(' ', '0')
    return version[:digit]


def hversions(seq, type='major'):
    """ Returns a list of versions selected depending on its types (major, minor, patch)
    """
    _versions = {}
    _result = []

    if '.' in seq[0]:
        f = _major if type == 'major' else _minor if type == 'minor' else _patch
        for v in reversed(seq):
            ver = f(v)
            if ver not in _versions:
                _versions[ver] = v
                _result.append(v)
    else:
        digit = -3 if type == 'major' else -2 if type == 'minor' else -1
        f = _version
        for v in reversed(seq):
            ver = f(v, digit)
            if ver not in _versions:
                _versions[ver] = v
                _result.append(v)

    _result = list(reversed(_result))
    # print '+++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
    # print 'HIERARCHICAL VERSIONS: ', _result
    # print '+++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
    return _result


def hierarchical_versions(seq, type='major'):
    """ Returns a list of versions selected depending on its types (major, minor, patch)
    """
    _versions = OrderedDict()

    if '.' in seq[0]:
        f = _major if type == 'major' else _minor if type == 'minor' else _patch
        for v in reversed(seq):
            ver = f(v)
            if ver not in _versions:
                _versions[ver] = v

    else:
        digit = -3 if type == 'major' else -2 if type == 'minor' else -1
        f = _version
        for v in reversed(seq):
            ver = f(v, digit)
            if ver not in _versions:
                _versions[ver] = v

    return OrderedDict(zip(reversed(_versions.keys(), _versions.values())))

def majors(seq):
    return hversions(seq, type='major')


def minors(seq):
    return hversions(seq, type='minor')


def patchs(seq):
    return hversions(seq, type='patch')


def take(seq, p):
    """ Takes p values in a sequence seq.
    With the first and last value.
    """
    n = len(seq)
    step = n / (p - 1)
    values = [seq[0]]
    indices = range(step, n - step + 1, step)[-p + 2:]
    values.extend([seq[i] for i in indices])
    if values[-1] != seq[-1]:
        values.append(seq[-1])

    return values
