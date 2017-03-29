# Tutorial: Testing conda packages with Version Climber

## Overview
In this tutorial, you will learn how to use VersionClimber when your script depends on conda packages that are already available. 
The first step is to define a configuration file. Then, you will have to adapt the original conda recipes. 
Finally, VersionClimber will find automatically the correct version of each package.

## Before you start

You should already have installed [Miniconda](https://conda.io/docs/install/quick.html) or 
[Anaconda](https://docs.continuum.io/anaconda/install).

Install VersionClimber:

```bash
python setup.py install --user=$CONDA_PREFIX
```

Now you are ready to define a configuration file for VersionClimber.

## Definition of a simple configuration file

VersionClimber use declarative configuration file to indicate which packages have to be tested and how.

In this section you are going to define a configuration file that use two rather complex conda packages, namely boost and protobuf.

The configuration file is as follow:
```yaml
packages:
    - name      : boost
      vcs       : git
      url       : https://github.com/boostorg/boost.git
      cmd       : conda build recipes/boost
      conda     : True
      recipe    : recipes/boost
      hierarchy : minor

    - name      : protobuf
      vcs       : git
      url       : https://github.com/google/protobuf.git
      cmd       : conda build recipes/protobuf
      conda     : True
      recipe    : recipes/protobuf
      hierarchy : minor

run:
    - python test_function.py
```
