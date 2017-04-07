package:
    name: protobuf
    version: "$version"
source:
    path : ../../.vclimb/protobuf
build:
    number: 0
    # skip the windows python 2.7 and 3.4 build
    # see https://github.com/google/protobuf/issues/1958
    features:
        - vc9                # [win and py27]
        - vc10               # [win and py34]
        - vc14               # [win and py35]

requirements:
    build:
        - git
        - cmake              # [win]
        - autoconf           # [unix]
        - automake           # [unix]
        - libtool            # [unix]
        - pkg-config         # [unix]
        - zlib 1.2.*
        - python
        - setuptools
        - six
        - ordereddict        # [py26]
        - unittest2          # [py26]

    run:
        - zlib 1.2.*
        - python
        - setuptools
        - six
        - ordereddict        # [py26]
        - unittest2          # [py26]

about:
    home: https://developers.google.com/protocol-buffers/
    license: New BSD License
    summary: Protocol Buffers - Google's data interchange format

extra:
    recipe-maintainers:
        - dopplershift
        - jakirkham
        - jjhelmus
        - ocefpaf
