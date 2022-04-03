from setuptools import setup

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='oresat-gps',
    version='0.1.2',
    author='PSAS',
    author_email='oresat@pdx.edu',
    license='GPL-3.0',
    description='OreSat GPS app.',
    long_description=long_description,
    maintainer='PSAS',
    maintainer_email='oresat@pdx.edu',
    url='https://github.com/oresat/oresat-gps-software',
    packages=['oresat_gps'],
    install_requires=[
        'pydbus'
    ],
    entry_points={
        'console_scripts': [
            'oresat-gps = oresat_gps.main:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    ],
)
