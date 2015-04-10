#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import find_packages, setup

VERSION = '0.1'

setup(
    name='cla_public',
    version=VERSION,
    author='MOJ',
    author_email='',
    url='https://github.com/ministryofjustice/cla_public',
    packages=find_packages(),
    include_package_data=True,
    license="MIT",
    zip_safe=False,
    keywords='cla_public',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
    ],
)
