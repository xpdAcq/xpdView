"""
use 'python setup.py install' while in file folder and anaconda is active to install this package, also user needs to
have the xray_vision package found here:
https://github.com/Nikea/xray-vision
Also need to install tifffile and pyqt (for some reason conda won't install these packages automatically). 
For tifffile installation instructions are on their website.
"""

from setuptools import setup, find_packages

setup(
    name='xpdview',
    version='0.1.0',
    packages=find_packages(),
    description='Visualization Code for Beam line',
    zip_safe=False,
    url='https://github.com/chiahaoliu/xpdView.git',
    install_requires=['numpy', 'tifffile',
                      'matplotlib>=2.0.0',
                      'pyqt>=4.11.4']
)
