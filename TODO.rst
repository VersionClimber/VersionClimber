This file can be used to document future development

   * Add OpenAlea and PlantGL examples.
   * Documentation in Sphinx and README
   * Extend VersionClimber configuration with pre and post steps

Add **post-install step** that construct from the winning configuration:
  - conda export environment -> mac app (conda)
  - A docker file: trace the different steps to obtain a given configuration
      - add an option to the vclimb command line

**Documentation**
- Sphinx (use pkglts)
- PyPi (pip install VersionClimber)

**Use template using conda build 3**
 - https://www.continuum.io/blog/developer-blog/package-better-conda-build-3

**Panta example**

Roadmap

27/10
  - travis and version climber
  - infraphenogrid:
    - matplotlib
    - openalea
    - openalea-components

03/11
  - Panta example

24/11
  - export environment with compiler

08/12
  - Add AppVeyor CI
