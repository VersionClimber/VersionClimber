package:
  name: openalea.phenomenal
  version: "$version"

source:
  path: ../../.vclimb/openalea.phenomenal

build:
  features:
    - vc9               [win and py27]
    - vc14              [win and py36]
  track_features:
    - vc9               [win and py27]
    - vc14              [win and py36]
  number: 0
  preserve_egg_dir: True
  string: phenomenal
  script:
    - python setup.py install --single-version-externally-managed --record record.txt

requirements:
  build:
    - python
    - setuptools
    - openalea.deploy
    - cython
    - numpy

  run:
    - python
    - numpy
    - numba
    - cython
    - openalea.deploy
    - scipy
    - scikit-image
    - scikit-learn
    - networkx
    - opencv
    - matplotlib
    - vtk
    - pywin32 [win]
    - nose
    - coverage
    - sphinx

# test:
#   imports:
#     - openalea.phenomenal
#     - openalea.phenomenal.calibration
#     - openalea.phenomenal.data
#     - openalea.phenomenal.display
#     - openalea.phenomenal.image
#     - openalea.phenomenal.mesh
#     - openalea.phenomenal.multi_view_reconstruction
#     - openalea.phenomenal.object
#     - openalea.phenomenal.segmentation

#   script: nosetests test

about:
  home: https://github.com/openalea/phenomenal
  license: Cecill-C License
  license_file: LICENSE.txt

extra:
  recipe-maintainers:
    - artzet-s
