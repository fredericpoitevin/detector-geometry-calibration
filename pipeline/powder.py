"""
params:
    - exp 
    - run 
    - noe 
    - dir 
    - tag
"""

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-exp", "--exp", help="experiment name",default=None, type=str)
parser.add_argument("-run", "--run", help="run number list",default=None, type=str)
parser.add_argument("-dir", "--dir", help="directory to setup",default="./", type=str)
parser.add_argument("-noe", "--noe", help="number of patterns",default=3000, type=int)
parser.add_argument("-tag", "--tag", help="tag to of save",default="", type=str)
parser.add_argument("-wait", "--wait", help="tag to of save",default="True", type=str)
args = parser.parse_args()


# diagnose input variables
from util import get_run
rlist = get_run(args.run)


# special cases
assert args.exp is not None


# process
from script.glance import Powder

powder = []
for run in rlist:
    powder.append(Powder(args.exp,run,outDir=args.dir,tag=args.tag))
    powder[-1].launch()

if args.wait.lower() in ["1","true","yes","t"]:
    for p in powder:
        p.wait()

powder = None