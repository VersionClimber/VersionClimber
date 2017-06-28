VersionClimber
==============

**Authors** : Christophe Pradal, Sarah Cohen-Boulakia, Patrick Valduriez, Dennis Shasha

**Institutes** : CIRAD / INRIA / NYU

**Status** : Python package

**License** : Cecill-C


About
-----

Description
+++++++++++

Version Climber is a system for package evolution for Data Science.

VersionClimber will help you upgrade a multi-package software
system to a version that works.


Content
+++++++

The Version Climber package contains :


Installation
------------


Installation
++++++++++++

Installing conda
*****************

You should already have installed `Miniconda <https://conda.io/docs/install/quick.html>`_ or
`Anaconda <https://docs.continuum.io/anaconda/install>`_ for Python 2.7.


Using conda on Linux, Mac or Windows
*************************************

::

    conda install versionclimber -c openalea


Using pip
**********

::

    pip install git+https://github.com/VersionClimber/VersionClimber


From the source code
*********************

::

    python setup.py install

Source code Requirements:

::

    pip install ipython
    pip install path.py
    pip install gitpython
    pip install pyyaml

    # optional
    pip install virtualenv



Usage
+++++

::

    vclimb --help

Documentation
-------------

You as the user have to do the following:

1. For each package in your system,
  you have to provide access to the versions you want VersionClimber to consider
  in conda.

  VersionClimber can build packages under **git** or **subversion**.

  VersionClimber can consider also **binary** packages released on public repository such as `PyPi <https://pypi.python.org/pypi>`_ or       `conda-forge <https://conda-forge.github.io/>`_.

  The versions of a package are formed by all the commits on *git* or *svn*. 
  However, if the package have been released and versionned with `Semantic Versionning <http://semver.org/>`_, these tags can be retrieve   and version can be explored hierarchically.


2. Order the packages from highest priority to lowest where more recent
  versions of higher priority packages are preferred over more recent
  versions of lower priority ones.


3. Installing VersionClimber as follows ::

    conda create -n tutorial_vclimb python2
    source activate tutorial_vclimb
    conda install versionclimber -c openalea
    conda install numpy scipy cython


4. Invoke VersionClimber as follows::

    vclimb


Case Study 1: simple two python packages from github
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

To run this case study, first create a new conda environment, and install VersionClimber.

Now you are ready to define a configuration file for VersionClimber.

Classical layout of a project
******************************

To reproduce an execution by using VersionClimber, you will create a directory containing two files.
Let's name this directory tutorial.
It will contain:

- **config.yaml:** the VersionClimber configuration file
- **test_function.py:** a executable script (python file or another script) to test the validity of one configuration

Definition of a simple configuration file
*****************************************

VersionClimber uses the declarative configuration file to indicate which packages have to be tested and how.

In this section you are going to define a configuration file that uses two well-knowned scientific Python packages, namely Scikit-Learn and Scikit-Image.

The configuration file `config.yaml <https://github.com/VersionClimber/VersionClimber/blob/conda/example/tuto11/config.yaml>`_ is as follow (here scikit-image has a higher priority than scikit-learn because scikit-image comes first):

::

    packages:
        - name      : scikit-image
          vcs       : git
          url       : https://github.com/scikit-image/scikit-image
          cmd       : pip install --no-index --no-deps -U
          version   : v0.11.0
          hierarchy : patch
          directory : .vclimb

        - name      : scikit-learn
          vcs       : git
          url       : https://github.com/scikit-learn/scikit-learn
          cmd       : pip install --no-index --no-deps -U
          version   : 0.16.0
          hierarchy : patch

    run:
        - python test_function.py


It is divided into two sections, namely **packages** and **run**:
- **packages:** list the different packages, their location (e.g. git repository), how to build them and which git commit or tags will be considered (in hierarchy, as explained below).
- **run:** indicate how to test the different packages together to know if one combination is valid. Typically (as in this example), this will be the name of a driver file.


Packages
********

The *packages* section list the different packages that will be tested by the run command:
    - **name** is the name of the package
    - **vcs** define which type of version control system the package use (i.e. git or svn).

If we want to consider binary packages rather than source one, we can define a package repository (i.e. pypi or conda)
    - **url** is the address where the package will be cloned or checkout
    - **cmd** is the command to build the package
    - **conda** is an optional argument to indicate if the package is managed by conda (`True`) or pip (`False`)
    - **recipe** is the local path where the conda recipe is defined
    - **channels** is a list of priority channels to consider when installing with conda
    - **hierarchy** is the strategy use to select the different versions of the package from the *vcs*.

If *hierarchy* is `major`, `minor`, or `patch`, the versions of the tags will be selected for that indentation level and higher. Otherwise, (`commit`) all the commits of the origin or master branch will be tested by VersionClimber. In this example, because minor packages are of the  form x.y, VersionClimber will take the most recent patch associated with each x.y. So, if a package is identified as 5.4.3 and there is no higher patch number among the patches that begin with 5.4, then VersionClimber will select 5.4.3.


Run command in *config.yaml*
****************************

This is the script (usually) after run: in that file. In our example,
`python test_function.py`


Invocation of VersionClimber
****************************

vclimb -- will fetch the packages from git, retrieve all the versions, install each configuration (set of package-version pairs) suggested by the Version Climber software, then invoke the run part of the config.yaml on that installed configuration. The output is configuration that works sorted based on the priorities in config.yaml


If we want to vary all the main dependencies of **scikit-learn** and **scikit-image**, we can extend the config.yaml file with other packages obtained from PyPi:
::

    packages:
        - name      : scikit-image
          vcs       : git
          url       : https://github.com/scikit-image/scikit-image
          cmd       : pip install --no-index --no-deps -U
          version   : v0.11.0
          hierarchy : patch
          directory : .vclimb

        - name      : scikit-learn
          vcs       : git
          url       : https://github.com/scikit-learn/scikit-learn
          cmd       : pip install --no-index --no-deps -U
          version   : 0.16.0
          hierarchy : patch

        - name      : scipy
          vcs       : pypi
          version   : 0.13.0
          hierarchy : minor

        - name      : numpy
          vcs       : pypi
          version   : 0.9.6
          hierarchy : minor

    run:
        - python test_function.py


All the minor versions of numpy and scipy will be considered (0.19, 0.18, ...). In this case, if wheels are availables, they will be installed in priority (thanks to pip).


Case Study 2: simple two packages both in python from conda
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

In this example, we consider the same packages that in the previous case study (i.e. scikits-learn and scikit-image),
but conda binary versions of the packages will be assemble rather than building the packages from github.

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

In this example, the set of versions of each package is retrieve from anaconda default channel and the conda-forge (ref TODO) one.
You can explore the available versions using the command

::

    vclimb --versions

.. TODO:: Give the output of vclimb

Like in the previous case study, we can extend the configuration file by adding numpy and scipy packages, but installed from conda.
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


Case Study 3: OpenAlea
+++++++++++++++++++++++++

In this case study, we want to found a valid configurationof various packages from OpenAlea, a scientific project developed to study multiscale plant modelling.

Packages in OpenAlea are implemented in different languages (mainly, C++, Python and R).
First, we will consider PlantGL (ref TODO), a large 3D C++ library with various dependencies.
Then we will explore an example obtained from the combina



What happens?
    - First, the different packages are checkout in the folder ``.vclimb``
    - Then, all the package versions are retrieved from git, PyPi or svn
    - The cmd (run) is tested on several configurations (combinations of packages)
    - The log is written in a file names versionclimber.log
