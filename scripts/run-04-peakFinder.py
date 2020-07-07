import peakfinderHelper as pfHelper
import subprocess 
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-exp", "--exp", help="experiment name", default="", type=str)
parser.add_argument("-run", "--run", help="run number", default="", type=str)
parser.add_argument("-det", "--det", help="detector alias (e.g. DscCsPad)", default=None, type=str) 
parser.add_argument("-pkTag", "--pkTag", help="tag of cxi file", default="", type=str) 
parser.add_argument("-noe", "--noe", help="number of images", default=-1, type=int)
parser.add_argument("-outDir", "--outDir", help="out dir", default=None, type=str)
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
    pf = pfHelper.peakFinderHelper(args.exp, run, args.det, args.outDir)
    pf.setDefaultParams()
    pf.setAdaptiveMode()
    pf.pkTag = args.pkTag 
    pf.noe = args.noe

    command = pf.getCommand()
    print " #####\n", command, "\n ######"

    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    out, err = process.communicate()
    print out
