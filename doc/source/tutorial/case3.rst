Case Study 3: OpenAlea
+++++++++++++++++++++++++

In this case study, we want to find a valid configuration of various packages from OpenAlea, a scientific project developed to study multiscale plant modeling.

Packages in OpenAlea are implemented in different languages (mainly, C++, Python and R).
First, we will consider PlantGL (ref TODO), a large 3D C++ library with various dependencies.
Then we will explore an example obtained from the combina



What happens?
    - First, the different packages are checked out in the folder ``.vclimb``
    - Then, all the package versions are retrieved from git, PyPi or svn
    - The cmd (run) is tested on several configurations (combinations of packages)
    - The log is written in a file names versionclimber.log
