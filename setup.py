"""
use 'python setup.py install' while in file folder and anaconda is active to install this package, also user needs to
have the xray_vision package found here:
https://github.com/Nikea/xray-vision
Also need to install tifffile and pyqt (for some reason conda won't install these packages automatically)
"""

from setuptools import setup, find_packages

setup(
    name='xpd_view',
    version='0.2',
    packages=find_packages(),
    description='Visualization Code for Beam line',
    zip_safe=False,
    url='https://github.com/cduff4464/xpdView.git',
    install_requires=['matplotlib', 'numpy', 'scipy', 'pyFAI']
)
