"""
params:
    - exp 
    - run 
    - tag 
    - powder
    - inp_fcrystfel
    - out_fcrystfel 
        - save new crystfel geom file
"""

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-exp", "--exp", help="experiment name",default=None, type=str)
parser.add_argument("-run", "--run", help="run number list",default=None, type=str)
parser.add_argument("-dir", "--dir", help="directory to setup",default="./", type=str)
parser.add_argument("-tag", "--tag", help="tag to of save",default="", type=str)
parser.add_argument("-powder", "--powder", help="",default=None, type=str)
parser.add_argument("-inp_fcrystfel", "--inp_fcrystfel", help="",default=None, type=str)
parser.add_argument("-out_fcrystfel", "--out_fcrystfel", help="",default=None, type=str)
args = parser.parse_args()


# diagnose input variables


# special cases
assert args.inp_fcrystfel is not None
assert args.out_fcrystfel is not None
mode1 = bool(args.exp and args.run) 
mode2 = bool(args.powder)
assert mode1 or mode2


# process
import os,sys 
import numpy as np 
from script.center import Center 
from script.geom import Geometry
from core.experiment import Exp

if mode1:
    # data from exp+run+dir
    powder = "" 
    if not os.path.isfile(powder):
        exit(1)
    _powderImg = np.load(powder)
    _mask = Exp(args.exp,int(args.run))
    cx,cy = Center.powder_optimize(_powderImg, _mask=_mask, logarithm=False, guessRow=None, guessCol=None,_range=100)
    print("New center(px) = (%d,%d)"%(cx,cy))
    Geometry.crystfel_to(src=args.inp_fcrystfel,dst=args.out_fcrystfel,cx_px=cx,cy_px=cy)
elif mode2:
    # data from powder file
    powder = args.powder
    if not os.path.isfile(powder):
        exit(1)
    
    _powderImg = np.load(powder)
    _mask = None
    _cutoff = True
    if os.path.isfile(args.mask):
        _mask = np.load(args.mask)
        _cutoff = False

    cx,cy = Center.powder_optimize(_powderImg, _mask=_mask, _cutoff=_cutoff, logarithm=False, guessRow=None, guessCol=None,_range=100)
    print("New center(px) = (%d,%d)"%(cx,cy))
    Geometry.crystfel_to(src=args.inp_fcrystfel,dst=args.out_fcrystfel,cx_px=cx,cy_px=cy)
else:
    exit(1)

