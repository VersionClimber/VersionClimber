""" Version utilities

"""


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


def _hversions(seq, type='major'):
    """ Returns a list of versions selected depending on its types (major, minor, patch)
    """
    _versions = {}
    _result = []

    if '.' in seq[0]:
        f = _major if type == 'major' else _minor if type == 'minor' else _patch
        for v in seq:
            ver = f(v)
            if ver not in _versions:
                _versions[ver] = v
                _result.append(v)
    else:
        digit = -3 if type == 'major' else -2 if type == 'minor' else -1
        f = _version
        for v in seq:
            ver = f(v, digit)
            if ver not in _versions:
                _versions[ver] = v
                _result.append(v)

    return _result


def majors(seq):
    return _hversions(seq, type='major')


def minors(seq):
    return _hversions(seq, type='minor')


def patchs(seq):
    return _hversions(seq, type='patch')
