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


Content
+++++++

The Version Climber package contains :


Installation
------------


Requirements
++++++++++++

::

    pip install ipython
    pip install path.py
    pip install gitpython
    pip install pyyaml

    # optional
    pip install virtualenv


Installation
++++++++++++

::

    python setup.py install

Usage
+++++



Documentation
-------------

Create a virtual environment
++++++++++++++++++++++++++++

(see http://docs.python-guide.org/en/latest/dev/virtualenvs/)

::

    $ cd my_project_folder
    $ virtualenv venv
    $ source venv/bin/activate

Install VersionClimber
++++++++++++++++++++++

::

    python setup.py install


YAML specification for VersionClimber
+++++++++++++++++++++++++++++++++++++

Define a file called config.yaml:

::

    packages:
        - name      : scikit-image
          vcs       : git
          url       : https://github.com/scikit-image/scikit-image
          cmd       : pip install --no-index --no-deps -U
          version   : v0.11.0
          hierarchy : patch
          directory : /Users/pradal/devlp/git_cache

        - name      : scikit-learn
          vcs       : git
          url       : https://github.com/scikit-learn/scikit-learn
          cmd       : pip install --no-index --no-deps -U
          version   : 0.16.0
          hierarchy : patch
          directory : /Users/pradal/devlp/git_cache

    run:
        - python my_script.py

Running Version Climber
+++++++++++++++++++++++

To run version climber, just run the following command::

    $ vclimb

What happens?
    - First, the different packages are checkout in the folder ``.vclimb``
    - Then, all the package versions are retrieved from git, PyPi or svn
    - The cmd (run) is tested on several configurations (combinations of packages)
    - The log is written in a file names versionclimber.log
