Case Study 1:  two python packages from github
===============================================

This case study is defined `here <https://github.com/VersionClimber/VersionClimber/tree/master/example/tuto_usecase1>`_.
To run this case study, first create a new conda environment, and install VersionClimber::

    conda create -n tutorial_usecase1 python=2 -y
    source activate tutorial_usecase1
    conda install versionclimber -c openalea -y

We install also some dependencies we want to fix, such as NumPy, SciPy, Cython and six::

    conda install numpy scipy cython six -y


Now you are ready to define a configuration file for VersionClimber in a directory.

Classical layout of a project
******************************

To reproduce an execution by using VersionClimber, you will create a directory containing two files.
Let's name this directory tutorial.
It will contain:

- `config.yaml <https://github.com/VersionClimber/VersionClimber/blob/master/example/tuto_usecase1/config.yaml>`_: the VersionClimber configuration file
- `test_function.py <https://github.com/VersionClimber/VersionClimber/blob/master/example/tuto_usecase1/test_function.py>`_: a executable script (python file or another script) to test the validity of one configuration

Definition of a simple configuration file
*****************************************

VersionClimber uses the declarative configuration file to indicate which packages have to be tested and how.

In this section you are going to define a configuration file that uses two well-knowned scientific Python packages, namely Scikit-Learn and Scikit-Image.

The configuration file `config.yaml <https://github.com/VersionClimber/VersionClimber/blob/master/example/tuto_usecase1/config.yaml>`_ is as follows (in this example, scikit-image has a higher priority than scikit-learn so scikit-image is first):

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

This is the script (usually) after run: in that `file  <https://github.com/VersionClimber/VersionClimber/blob/master/example/tuto_usecase1/test_function.py>`_

This script (*test_function.py*) extract HOG features of each digits of the MNIST database of handwritten digits using scikit-image and train a Linear SVM classifier to recognise hand-written digits.


Invocation of VersionClimber
****************************

**vclimb** -- will fetch the packages from git, retrieve all the versions, install each configuration (set of package-version pairs) suggested by the Version Climber software, then invoke the run part of the config.yaml on that installed configuration. The output is configuration that works sorted based on the priorities in config.yaml


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

