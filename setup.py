from setuptools import setup, find_packages

setup(
    name='xpdview',
    version='0.4.0',
    packages=find_packages(),
    description='Visualization Code for Beam line',
    zip_safe=False,
    url='https://github.com/xpdAcq/xpdView.git',
    install_requires=['numpy', 'matplotlib',
                      'scipy',
                      'tifffile']
)
