"""
params:
    - exp
    - run
    - dir
    - noe
    - pktag
"""

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-exp", "--exp", help="experiment name",default=None, type=str)
parser.add_argument("-run", "--run", help="run number list",default=None, type=str)
parser.add_argument("-dir", "--dir", help="directory to setup",default="./", type=str)
parser.add_argument("-pktag", "--pktag", help="tag to of save",default="", type=str)
parser.add_argument("-noe", "--noe", help="",default=None, type=int)
parser.add_argument("-wait", "--wait", help="",default="False", type=str)
args = parser.parse_args()


# diagnose input variables
from util import get_run
rlist = get_run(args.run)

# special cases
assert args.exp is not None


# process
import os,sys 
import numpy as np 
from script.peakf import PeakFinder

pf = []
for run in rlist:
    pf.append(PeakFinder( expName=args.exp,runNumber=run,detName=None,outDir=args.dir or os.path.realpath("./") ))
    pf[-1].launch()

if self.wait.lower() in ["1","yes","y","true","t"]:
    for p in pf:
        p.wait()

for p in pf:
    p = None
