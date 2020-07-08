import setuptools
from io import open

requirements = [
    'numpy',
    'scipy',
    'pytest',
    'matplotlib',
    'setuptools'
]

setuptools.setup(name='autosfx',
      maintainer='Zhen Su',
      version='0.0.1',
      maintainer_email='zhensu@stanford.edu',
      description='LCLS SFX Automation.',
      long_description=open('README.md', encoding='utf8').read(),
      url='https://github.com/fredericpoitevin/autosfx.git',
      packages=setuptools.find_packages(),
      install_requires=requirements,
      classifiers=[
          "Programming Language :: Python :: 3",
          "Operating System :: OS Independent",
      ],
      zip_safe=False)
