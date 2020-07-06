"""
params:
    - cxi
    - exp
    - run
    - dir
    - pktag
    - dxtag
    - fcell
    - likelihood
"""

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-exp", "--exp", help="",default=None, type=str)
parser.add_argument("-run", "--run", help="",default=None, type=str)
parser.add_argument("-dir", "--dir", help="",default="./", type=str)
parser.add_argument("-cxi", "--cxi", help="",default=None, type=str)
parser.add_argument("-pktag", "--pktag", help="",default="", type=str)
parser.add_argument("-dxtag", "--dxtag", help="",default="", type=str)
parser.add_argument("-fcell", "--fcell", help="",default=None, type=str)
parser.add_argument("-fcrystfel", "--fcrystfel", help="",default=None, type=str)
parser.add_argument("-likelihood", "--likelihood", help="",default=0, type=float)
args = parser.parse_args()


# diagnose input variables
from util import get_run
rlist = get_run(args.run)

# special cases
mode1 = bool(args.exp and args.run)
mode2 = bool(args.cxi and args.fcrystfel)
assert mode1 or mode2

# process
import os,sys 
import numpy as np 
from script.indexer import IndexerServer


indexer = []
if mode1:
    # accept exp+run+dir
    for run in rlist:
        outDir = os.path.realpath(args.dir or "./")
        runDir = Path(args.exp,run,outDir).runDir
        fcxi = Path(args.exp,run,outDir).peakf(tag=pktag).fcxi
        fcrystfel = args.fcrystfel or Path(args.exp,run,outDir).fgeom

        indexer.append( IndexerServer(cxiList=[fcxi],fcell=args.fcell,outDir=runDir,fcrystfel=fcrystfel,likelihood=args.likelihood) )
        indexer[-1].launch()
elif mode2:
    indexer.append( IndexerServer(cxiList=[args.cxi],fcell=args.fcell,outDir=args.dir,fcrystfel=args.fcrystfel,likelihood=args.likelihood) )
    indexer[-1].launch()
else:
    exit(1)


for dx in indexer:
    dx.wait()
    dx.merge()

