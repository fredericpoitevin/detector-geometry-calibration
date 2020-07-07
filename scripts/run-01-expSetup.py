from expSetup import setupNewRun
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-exp", "--exp", help="experiment name", default="", type=str)
parser.add_argument("-run", "--run", help="run number", default="", type=str)
parser.add_argument("-det", "--det", help="detector alias (e.g. DscCsPad)", default=None, type=str) 
parser.add_argument("-outDir", "--outDir", help="detector alias (e.g. DscCsPad)", default=None, type=str) 
parser.add_argument("-copyRun", "--copyRun", help="copy setup from runNumber", default=None, type=int) 
args = parser.parse_args() 

def get_run(runs):
    rlist = []
    for each in runs.split(","):
        if each == "":
            continue
        elif ":" in each:
            start,end = each.split(":")
            rlist.extend(range(int(start),int(end)+1))
        else:
            rlist.append(int(each))
    return rlist

if args.det is None:
    from experiment import myExp
    runs = get_run(args.run)
    exp = myExp(args.exp,runs[0])
    try: exp.Det
    except: pass 
    args.det = exp.detName
    print args.det 

for run in get_run(args.run):
    if run == args.copyRun:
        setupNewRun(experimentName = args.exp, runNumber = run, detectorName=args.det, outDir = args.outDir)
    else:
        setupNewRun(experimentName = args.exp, runNumber = run, detectorName=args.det, outDir = args.outDir, copyRun=args.copyRun)
