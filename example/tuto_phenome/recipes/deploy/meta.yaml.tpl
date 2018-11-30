package:
  name: openalea.deploy
  version: "$version"

source:
  path: ../../.vclimb/openalea.deploy

build:
  preserve_egg_dir: True
  number: 0
  script: python setup.py install

requirements:
  build:
    - python
    - setuptools
    - pywin32 # [win]
    - six
  run:
    - python
    - setuptools
    - pywin32 # [win]
    - six
    - path.py


about:
  home: http://github.com/openalea/deploy
  license: Cecill-C License
  summary: OpenAlea.Deploy support the installation of OpenAlea packages via the network and manage their dependencies.