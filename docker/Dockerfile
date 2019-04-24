FROM continuumio/miniconda3

RUN conda create -n cise -c versionclimber versionclimber -y
RUN source activate cise
RUN conda remove versionclimber -y
RUN git clone https://github.com/VersionClimber/VersionClimber
RUN python VersionClimber/setup.py develop

