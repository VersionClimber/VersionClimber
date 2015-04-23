#!/usr/bin/env python
import os

versions = ['0.12','0.14']

cmd_str = 'pip install --upgrade git+https://github.com/scikit-learn/scikit-learn@%s'

for i, version in enumerate(versions):
    os.system(cmd_str%version)
    print 'Install Scikit Learn version ', version
    os.system('cd vm%d'%(i+1))
    os.system('reprozip trace python ../plot_digits_classification.py')
    os.system('cd ..')


