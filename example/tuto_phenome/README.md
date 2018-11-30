# Tutorial: Testing conda packages with Version Climber

## Overview
In this tutorial, you will learn how to use VersionClimber when your script depends on conda packages that are already available (i.e. you don't need to create new recipes).
The first step is to define a configuration file which will include the priorities of different packages.
Then, you will have to adapt the original conda recipes.
Finally, VersionClimber will automatically find a configuration that works having the highest version of each package in (package) priority order. So the highest version possible of the highest priority package, then the highest version of the next highest priority package etc.

## Before you start

You should already have installed [Miniconda](https://conda.io/docs/install/quick.html) or
[Anaconda](https://docs.continuum.io/anaconda/install) for Python 2.7.

Create an new conda environment:

```bash
conda create -n vclimber -y python
```

Install VersionClimber:

```bash
conda install -c versionclimber versionclimber
```

Now you are ready to define a configuration file for VersionClimber.

## Classical layout of a project

To reproduce an execution by using VersionClimber, you will create a directory containing two files and a directory.
Let's name this directory tutorial. It will contain:
- **config.yaml:** the VersionClimber configuration file
- **test_function.py:** a python file (or another script) to test the validity of one configuration
- **recipes: ** a directory that will contain one recipe per dependency package.

## Definition of a simple configuration file

VersionClimber uses the declarative configuration file to indicate which packages have to be tested and how.

In this section you are going to define a configuration file that uses two rather complex conda packages, namely boost and protobuf.

The configuration file [config.yaml](https://github.com/pradal/VersionClimber/blob/conda/example/tuto_conda01/config.yaml) is as follow (here boost has a higher priority than protobuf because boost comes first):
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
- **packages:** list the different packages, their location (e.g. git repository), how to build them and which git commit or tags will be considered (in hierarchy, as explained below).
- **run:** indicate how to test the different packages together to know if one combination is valid. Typically (as in this example), this will be the name of a driver file.

### Packages

The *packages* section list the different packages that will be tested by the run command:
- **name** is the name of the package
- **vcs** define which type of version control system the package use (i.e. git or svn).
- **url** is the address where the package will be cloned or checkout
- **cmd** is the command to build the package
- **conda** is an optional argument to indicate if the package is managed by conda (`True`) or pip (`False`)
- **recipe** is the local path where the recipe is defined
- **hierarchy** is the strategy use to select the different versions of the package from the *vcs*.
If *hierarchy* is `major`, `minor`, or `patch`, the versions of the tags will be selected for that indentation level and higher. Otherwise, (`commit`) all the commits of the origin or master branch will be tested by VersionClimber. In this example, because minor packages are of the  form x.y, VersionClimber will take the most recent patch associated with each x.y. So, if a package is identified as 5.4.3 and there is no higher patch number among the patches that begin with 5.4, then VersionClimber will select 5.4.3.


### Run command in config.yaml

This is the script (usually) after run: in that file. In our example,
`python test_function.py`

## Adaptation of conda recipes for Version Climber

Conda recipes of major packages can be found on different repository, such as [conda-recipes](https://github.com/conda/conda-recipes).
In this example, we depends on two packages: [boost](http://www.boost.org) and [protobuf](https://developers.google.com/protocol-buffers).

VersionClimber needs modified conda recipes to build all the packages together locally from different versions of git source code.
All the modified recipes are located in the recipes directory.

### boost recipe

First, we get the [boost recipe](https://github.com/conda/conda-recipes/tree/master/boost) from conda-recipes.

The *meta.yaml* file is copied into a template file (named [*meta.yaml.tpl*](./recipes/boost/meta.yaml.tpl)) and is modified as follow:
```yaml
package:
  name: boost
  # OLD RECIPE version (remove it)
  version: 1.61.0 # To be replaced by:
  # NEW VersionClimber version
  version: "$version"

source:
  # OLD SOURCE LOCATION (remove it)
  fn:  boost_1_61_0.tar.bz2
  url: http://sourceforge.net/projects/boost/files/boost/1.61.0/boost_1_61_0.tar.bz2
  md5: 6095876341956f65f9d35939ccea1a9f

  # NEW VersionClimber SOURCE LOCATION
  path : ../../.vclimb/boost

build:
  features:

...
```

The **package** and the **source** sections are modified:
- **package**: the **version** variable must be equal to **"$version"**. VersionClimber will replaced the **"$version"** variable by the git tag or the git commit value.
- **source**: the **url** value is replaced by a local location where VersionClimber will clone the boost package (i.e. **../../.vclimb/boost**).



### Protobuf recipe

The [Protobuf recipe](https://github.com/conda-forge/protobuf-feedstock/blob/master/recipe) is retrieved from [conda-forge](https://github.com/conda-forge).

We simplify it by removing the header and the tests that can be done in the driver file. The [meta.yaml.tpl](./recipes/protobuf/meta.yaml.tpl) looks like :

```yaml
# REMOVE THESE LINES
# {% set name = "protobuf" %}
# {% set version = "3.2.0" %}
# {% set sha256 = "2a25c2b71c707c5552ec9afdfb22532a93a339e1ca5d38f163fe4107af08c54c" %}

package:
  name: "protobuf"
  # REPLACE
  version: {{ version }}
  # BY VERSIONCLIMBER template flag
  version : "$version"

source:
  # REPLACE
  fn: {{ name }}-{{ version }}.tar.gz
  url: https://github.com/google/protobuf/archive/v{{ version }}/{{ name }}-v{{ version }}.tar.gz
  sha256: {{ sha256 }}
  # BY new VERSIONCLIMBER protobuf location
  path : ../../.vclimb/protobuf

build:
  features:

...
# REMOVE ALL THE TEST  SECTION

#test:
#  commands:
#    - protoc --help
#    - test -f ${PREFIX}/lib/libprotobuf.a                           # [unix]
#    - test -f ${PREFIX}/lib/libprotobuf.dylib                       # [osx]
#    - test -f ${PREFIX}/lib/libprotobuf.so                          # [linux]
#    - if not exist %PREFIX%\\Library\\lib\\libprotobuf.lib exit 1   # [win]
#  imports:
#    - google
#    - google.protobuf
#    - google.protobuf.internal
#    - google.protobuf.pyext

about:
    home: https://developers.google.com/protocol-buffers/
    license: New BSD License
    summary: Protocol Buffers - Google's data interchange format

...
```



## Invocation of VersionClimber

vclimb -- will fetch the packages from git, retrieve all the versions, install each configuration (set of package-version pairs) suggested by the Version Climber software, then invoke the run part of the config.yaml on that installed configuration. The output is configuration that works sorted based on the priorities in config.yaml
