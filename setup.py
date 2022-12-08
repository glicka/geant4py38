#!/usr/bin/env python

from setuptools import find_packages, setup

# Package metadata.
NAME = 'geant4py'
DESCRIPTION = 'Geant4 simulation framework in Python'
URL = 'https://gitlab.com/glicka/geant4py38'
EMAIL = 'aeglick@mdanderson.org'
AUTHOR = 'Adam Glick'
REQUIRES_PYTHON = '>=3.8'
MAJOR = 0
MINOR = 1
MICRO = 0

# Version
VERSION = '{}.{}.{}'.format(MAJOR, MINOR, MICRO)

# Required packages
with open('requirements.txt', 'r') as fh:
    REQUIREMENTS = [l for l in fh.read().split('\n') if l]

# Setup
setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    download_url=URL,
    packages=find_packages(where='.'),
    platforms=['macOS', 'Linux'],
    install_requires=REQUIREMENTS,
    license='MIT',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',
        'Operating System :: MacOS'],
    include_package_data=True
)
