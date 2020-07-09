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

## Usage
```
autosfx  *command*
```
