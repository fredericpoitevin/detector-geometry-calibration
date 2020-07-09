import setuptools
from io import open

requirements = [
    'numpy',
    'h5py',
    'scipy',
    'setuptools'
]

setuptools.setup(name='autosfx',
                 version='0.0.1',
                 author='Zhen Su',
                 maintainer='Frederic Poitevin',
                 maintainer_email='fpoitevi@slac.stanford.edu',
                 description='LCLS SFX Automation.',
                 long_description=open('README.md', encoding='utf8').read(),
                 url='https://github.com/fredericpoitevin/autosfx.git',
                 packages=setuptools.find_packages(),
                 entry_points={
                     "console_scripts": [
                       "autosfx = autosfx.__main__:main",
                       ],
                 },
                 include_package_data = True,
                 install_requires=requirements
                )
