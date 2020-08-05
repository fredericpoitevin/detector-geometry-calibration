# geomcalib
LCLS SFX Automation - detector geometry calibration

## Installation 
Requires psana1 and python2. See `setup.py` for other requirements.

### at SLAC (on psana)
```
git clone https://github.com/fredericpoitevin/detector-geometry-calibration.git
cd detector-geometry-calibration
source /reg/g/psdm/etc/psconda.sh
python setup.py install --user
export PATH="/reg/neh/home5/${USER}/.local/bin:$PATH"
```

## Usage
### CLI
```bash
(ana-1.5.11) [fpoitevi@pslogin01 autosfx]$ geomcalib -h
usage: geomcalib [-h] [--version] {setup} ...

AutoSFX

optional arguments:
  -h, --help  show this help message and exit
  --version   show program's version number and exit

Choose a command:
  {setup}
```
### as a python module
```python
import geomcalib
geomcalib.__version__
```
