FROM continuumio/miniconda3

RUN conda install -c versionclimber versionclimber python=2.7 numpy scipy matplotlib notebook seaborn h5py nbconvert -y
RUN conda remove versionclimber -y
RUN git clone https://github.com/VersionClimber/VersionClimber.git VersionClimber
RUN cd VersionClimber; python setup.py develop; cd ..

