# Tutorial: Testing conda packages with Version Climber

## Overview
In this tutorial, you will learn how to use VersionClimber when your script depends on conda packages that are already available. 
The first step is to define a configuration file. Then, you will have to adapt the original conda recipes. 
Finally, VersionClimber will find automatically the correct version of each package.

## Before you start

You should already have installed [Miniconda](https://conda.io/docs/install/quick.html) or 
[Anaconda](https://docs.continuum.io/anaconda/install) for Python 2.7.

Create an new conda environment:

```bash
conda create -n vclimber -y python
```

Install VersionClimber:

```bash
python setup.py install --user=$CONDA_PREFIX
```

Now you are ready to define a configuration file for VersionClimber.

## Definition of a simple configuration file

VersionClimber use declarative configuration file to indicate which packages have to be tested and how.

In this section you are going to define a configuration file that use two rather complex conda packages, namely boost and protobuf.

The configuration file [config.yaml](https://github.com/pradal/VersionClimber/blob/conda/example/tuto_conda01/config.yaml) is as follow:
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

It is divided into two sections, namely **packages** and **run**:
- **packages:** list the different packages, their location (e.g. git repository), how to build them and which git commit or tags will be considered.
- **run:** indicate how to test the different packages together to know if one combination is valid.

### Packages

The *packages* section list the different packages that will be tested by the run command:
- **name** is the name of the package
- **vcs** define which type of version control system the package use (i.e. git or svn).
- **url** is the address where the package will be cloned or checkout
- **cmd** is the command to build the package
- **conda** is an optional argument to indicate if the package is managed by conda (`True`) or pip (`False`)
- **recipe** is the local path where the recipe is defined
- **hierarchy** is the strategy use to select the different versions of the package from the *vcs*. 
If *hierarchy* is `major`, `minor`, or `patch`, only the versions of the tags will be selected. Otherelse (`commit`) all the commits of the origin or master branch will be tested by VersionClimber.


### Run command

