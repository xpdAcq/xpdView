"""
use 'python setup.py install' while in file folder in anaconda to install this package
"""

from setuptools import setup, find_packages

setup(
    name='xpd_view',
    version='0.vista',
    packages=find_packages(),
    description='Visualization Code for Beam line',
    zip_safe=False,
    url='https://github.com/cduff4464/xpdView.git'
)
