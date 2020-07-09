# autosfx

LCLS SFX Automation

## Installation 
Requires psana1 and python2. See `setup.py` for other requirements.

### at SLAC (on psana)
```
git clone https://github.com/fredericpoitevin/autosfx.git
cd autosfx
source /reg/g/psdm/etc/psconda.sh
python setup.py install --user
export PATH="/reg/neh/home5/${USER}/.local/bin:$PATH"
```
### with Conda
Note: this will not work unless adapted to an environment pre-isntalled with psana. It might be useful to test though.
```
conda create -f environment.yml
conda activate autosfx
python setup.py install
``` 

## Usage
```
autosfx  *command*
```
