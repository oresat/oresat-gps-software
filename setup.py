from setuptools import setup

from oresat_gps import __version__

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='oresat-gps',
    version=__version__,
    author='PSAS',
    author_email='oresat@pdx.edu',
    license='GPL-3.0',
    description='OreSat GPS app',
    long_description=long_description,
    maintainer='PSAS',
    maintainer_email='oresat@pdx.edu',
    url='https://github.com/oresat/oresat-gps-software',
    packages=['oresat_gps'],
    keywords=['oresat', 'gps'],
    install_requires=[
        'oresat-olaf',
        'pyserial',
    ],
    entry_points={
        'console_scripts': [
            'oresat-gps = oresat_gps.__main__:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Software Development :: Embedded Systems',
    ],
)
