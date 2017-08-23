from setuptools import setup, find_packages

setup(
    name='xpdview',
    version='0.1.0',
    packages=find_packages(),
    description='Visualization Code for Beam line',
    zip_safe=False,
    url='https://github.com/chiahaoliu/xpdView.git',
    install_requires=['numpy', 'six', 'matplotlib',
                      # 'PyQt5', 'PyQt4',
                      'scipy',
                      'tifffile']
)
