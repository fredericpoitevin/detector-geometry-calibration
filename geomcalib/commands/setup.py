'''
Experiment setup
'''

import argparse

from geomcalib import expSetup

def add_args(parser):
    parser.add_argument("-exp", "--exp", help="experiment name", default="", type=str)
    parser.add_argument("-run", "--run", help="run number", default="", type=str)
    parser.add_argument("-det", "--det", help="detector alias (e.g. DscCsPad)", default=None, type=str) 
    parser.add_argument("-outDir", "--outDir", help="detector alias (e.g. DscCsPad)", default=None, type=str) 
    parser.add_argument("-copyRun", "--copyRun", help="copy setup from runNumber", default=None, type=int) 
    return parser

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

def main(args):

    if args.det is None:
        from geomcalib import experiment
        runs = get_run(args.run)
        exp = experiment.myExp(args.exp,runs[0])
        try: exp.Det
        except: pass 
        args.det = exp.detName
        print args.det 

    for run in get_run(args.run):
        if run == args.copyRun:
            expSetup.setupNewRun(experimentName = args.exp, runNumber = run, detectorName=args.det, outDir = args.outDir)
        else:
            expSetup.setupNewRun(experimentName = args.exp, runNumber = run, detectorName=args.det, outDir = args.outDir, copyRun=args.copyRun)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    main(add_args(parser).parse_args())
