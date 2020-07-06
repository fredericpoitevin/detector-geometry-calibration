import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-exp", "--exp", help="",default=None, type=str)
parser.add_argument("-run", "--run", help="",default=None, type=str)
parser.add_argument("-dir", "--dir", help="",default="./", type=str)
parser.add_argument("-cxi", "--cxi", help="",default=None, type=str)
parser.add_argument("-pktag", "--pktag", help="",default="", type=str)
parser.add_argument("-scan", "--scan", help="",default="distance+center", type=str)
parser.add_argument("-fcell", "--fcell", help="",default=None, type=str)
parser.add_argument("-inp_fcrystfel", "--inp_fcrystfel", help="",default=None, type=str)
parser.add_argument("-out_fcrystfel", "--out_fcrystfel", help="",default=None, type=str)
args = parser.parse_args()


# diagnose input variables
from util import get_run
rlist = get_run(args.run)

# get the cxi files


# fast search of top 100 / all 
import os,sys 
from script.distance import Distance

# Fast scan to check whether pattern is good
dman = Distance(cxiList=cxiList,outDir=outDir,fcell=args.fcell,fcrystfel=inp_fcrystfel)
result = dman.optimize_fast_scan(scan=args.scan,top=100,scan_center_px=5,scan_distz_mm=3) # scan on center+/-5px, distance+/-3mm
if not result.status:
    print("!! Can't index")
    exit(1)

# Fine scan to deploy 
dman = Distance(cxiList=cxiList,outDir=outDir,fcell=args.fcell,fcrystfel=result.fcrystfel)
result = dman.optimize_scan(scan="distance",top=100,scan_distz_mm=2) # scan on distance+/-2mm
if not result.status:
    print("!! Can't index")
    exit(1)

# Deploy center
dman = Distance(cxiList=cxiList,outDir=outDir,fcell=args.fcell,fcrystfel=result.fcrystfel)
result = dman.optimize_center(top=int(200/result.index_rate)) # scan on distance+/-2mm
if not result.status:
    print("!! Can't index")
    exit(1)

# Optimize distance
dman = Distance(cxiList=cxiList,outDir=outDir,fcell=args.fcell,fcrystfel=result.fcrystfel)
result = dman.optimize_distance(top=1000) # scan on distance+/-2mm
if not result.status:
    print("!! Can't index")
    exit(1)

print("## optimized geometry found ")
copyfile(result.fcrystfel,args.out_fcrystfel)