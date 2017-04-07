package:
  name: boost
  version: "$version"

source:
  path : ../../.vclimb/boost

build:
  features:
    - vc9               [win and py27]
    - vc10              [win and py34]
    - vc14              [win and py35]

requirements:
  build:
    - python
    - icu 54.*          [unix]
    - bzip2             [unix]
    - zlib

  run:
    # python dependency is here due to libboost-python library that depends on
    # python version
    - python
    - icu 54.*          [unix]
    - zlib

about:
  home: http://www.boost.org/
  license: Boost-1.0

