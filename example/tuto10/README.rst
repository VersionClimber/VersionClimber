Documentation of VersionClimber: Tutorial 10
=============================================

Create a virtual environment
++++++++++++++++++++++++++++

(see http://docs.python-guide.org/en/latest/dev/virtualenvs/)

::

    $ virtualenv venv
    $ source venv/bin/activate

Install VersionClimber
++++++++++++++++++++++

::

    $ cd ../..
    $ python setup.py install
    $ cd -

Read (and edit) the YAML specification file
++++++++++++++++++++++++++++++++++++++++++++


Edit the config.yaml file.
You can (or comment) packages, default version, ...

  * Test the script when installing the dependencies

::
    $ pip install -U pip
    $ pip install path.py
    $ pip install gitpython
    $ pip install pyyaml

    $ pip install scipy
    $ pip install scikit-learn
    $ pip install scikit-image
    $ pip install matplotlib

    $ python estimate_hog.py

Running Version Climber
+++++++++++++++++++++++

To run version climber, just run the following command::

    $ vclimb

