import findCenter as fc 
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-exp", "--exp", help="experiment name", default="", type=str)
parser.add_argument("-run", "--run", help="run number", default=-1, type=int)
parser.add_argument("-det", "--det", help="detector alias (e.g. DscCsPad)", default=None, type=str) 
parser.add_argument("-cx", "--cx", help="center x", default=None, type=float) 
parser.add_argument("-cy", "--cy", help="center y", default=None, type=float) 
args = parser.parse_args()

if args.det is None:
    from experiment import myExp
    runs = [args.run]
    exp = myExp(args.exp,runs[0])
    try: exp.Det
    except: pass 
    args.det = exp.detName
    print args.det 
    
    
if args.cx is None or args.cy is None:
    print "##### No input new center"
 
fc.deployCenter(experimentName=args.exp, runNumber=args.run, detectorName=args.det, newCx=args.cx, newCy=args.cy)
 