Installation with Miniconda
===========================

Conda installation
----------------------

You should already have installed `Miniconda <https://conda.io/docs/install/quick.html>`_ or
`Anaconda <https://docs.continuum.io/anaconda/install>`_ for Python 2.7.


Using **conda** on Linux, Mac or Windows
-----------------------------------------

Create virtual environment and activate it
..........................................

.. code:: shell

    conda create --name vclimber python
    source activate vclimber


Version Climber install
........................

.. code:: shell

    conda install -c versionclimber versionclimber

Installation with **pip**
==========================

::

    pip install git+https://github.com/VersionClimber/VersionClimber


Installation from source code
==================================

Source code Requirements (conda env)::

    conda install path.py gitpython pyyaml python six requests pyzmq

or (in a virtualenv)::

    pip install path.py gitpython pyyaml

Install from source VersionClimber::

    python setup.py install


