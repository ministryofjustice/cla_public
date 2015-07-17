#!/usr/bin/env bash

# INSTALL PYTHON 2.7.9
cd /tmp
wget https://www.python.org/ftp/python/2.7.9/Python-2.7.9.tgz
tar zxvf Python-2.7.9.tgz
cd Python-2.7.9
./configure && make && make install
cd /tmp && rm -rf Python-*

# INSTALL PYTHON SETUPTOOLS
wget https://pypi.python.org/packages/source/s/setuptools/setuptools-15.2.tar.gz#md5=a9028a9794fc7ae02320d32e2d7e12ee
tar zxvf setuptools-15.2.tar.gz
cd setuptools-15.2
/usr/local/bin/python2.7 setup.py install
cd /tmp && rm -rf setuptools*

# INSTALL PYTHON PIP
wget https://pypi.python.org/packages/source/p/pip/pip-6.1.1.tar.gz#md5=6b19e0a934d982a5a4b798e957cb6d45
tar zxvf pip-6.1.1.tar.gz
cd pip-6.1.1
/usr/local/bin/python2.7 setup.py install
