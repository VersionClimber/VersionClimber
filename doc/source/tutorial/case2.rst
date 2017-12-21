Case Study 2: Two binary packages available from conda
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

In this example, we consider the same packages that in the previous case study (i.e. scikit-learn and scikit-image),
but conda binary versions of the packages will be assembled rather than building the packages from github.

::

    packages:
        - name      : scikit-image
          vcs       : conda
          cmd       : conda install -y
          channels  :
            - conda-forge
          hierarchy : patch

        - name      : scikit-learn
          vcs       : conda
          cmd       : conda install -y
          channels  :
            - conda-forge
          hierarchy : patch

    run:
        - python test_function.py

In this example, the set of versions of each package is retrieved from anaconda default channel and the conda-forge (ref TODO) one.
You can explore the available versions using the command

::

    vclimb -v

    --------------------------------------------------------------------------------
    Versions of scikit-image scikit-learn


    Versions of  scikit-image
    ------------------------
    0.7.2
    0.8.0
    0.8.2
    0.9.1
    0.9.3
    0.10.0
    0.10.1
    0.11.0
    0.11.2
    0.11.3
    0.12.3
    0.13.0


    Versions of  scikit-learn
    ------------------------
    0.11
    0.12.1
    0.13
    0.13.1
    0.14.1
    0.15.0
    0.15.0b1
    0.15.0b2
    0.15.1
    0.15.2
    0.16.0
    0.16.1
    0.17
    0.17.1
    0.18
    0.18.1
    0.18.2

As in the previous case study, we can extend the configuration file by adding numpy and scipy packages, but installed from conda.
::

    packages:
        - name      : scikit-image
          vcs       : conda
          cmd       : conda install -y
          channels  :
            - conda-forge
          hierarchy : patch

        - name      : scikit-learn
          vcs       : conda
          cmd       : conda install -y
          channels  :
            - conda-forge
          hierarchy : patch

        - name      : scipy
          vcs       : conda
          cmd       : conda install -y
          channels  :
            - conda-forge
          hierarchy : minor

        - name      : numpy
          vcs       : conda
          cmd       : conda install -y
          channels  :
            - conda-forge
          hierarchy : minor

    run:
        - python test_function.py
