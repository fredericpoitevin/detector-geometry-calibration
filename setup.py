import setuptools
from io import open

requirements = [
    'numpy',
    'h5py',
    'scipy',
    'setuptools'
]

setuptools.setup(name='geomcalib',
                 version='0.0.1',
                 author='Zhen Su',
                 maintainer='Frederic Poitevin',
                 maintainer_email='fpoitevi@slac.stanford.edu',
                 description='LCLS SFX Automation: detector geometry calibration tools',
                 long_description=open('README.md', encoding='utf8').read(),
                 url='https://github.com/fredericpoitevin/detector-geometry-calibration.git',
                 packages=setuptools.find_packages(),
                 entry_points={
                     "console_scripts": [
                       "geomcalib = geomcalib.__main__:main",
                       ],
                 },
                 include_package_data = True,
                 install_requires=requirements
                )
