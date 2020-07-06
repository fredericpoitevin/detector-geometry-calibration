"""
params:
    - exp: experiment name.
        - cxic0415
    - dir: output directory.
        - ./
    - run: run number list.
        - 10-20,25,30-40
    - base: setup other runs based on this run. 
        - 10/None
"""

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-exp", "--exp", help="experiment name",default=None, type=str)
parser.add_argument("-run", "--run", help="run number list",default=None, type=str)
parser.add_argument("-dir", "--dir", help="directory to set up", default=None, type=str)
parser.add_argument("-base", "--base", help="setup other runs based on this run", default=None, type=int)
args = parser.parse_args()


# diagnose input variables
from util import get_run
rlist = get_run(args.run)


# special cases
assert args.exp is not None


# process
from script.setup import Setup
from core.parameters import Path

if isinstance(args.base,int):
    setup = Setup(expName=args.exp,runNumber=int(args.base),outDir=args.dir)
    setup.run_make()
    for run in rlist:
        if run != args.base:
            runPath = Path(args.exp,run,args.dir)
            runPath.dir_make()
            try:
                copyfile(setup.fgeom, runPath.fgeom)
                copyfile(setup.pmask, runPath.pmask)
                copyfile(setup.smask, runPath.smask)
            except:
                pass 
            runPath = None
else:
    for run in rlist:
        setup = Setup(expName=args.exp,runNumber=run,outDir=args.dir)
        setup.run_make()
        setup = None

