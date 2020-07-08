import indexerHelper as indexerHelper
import subprocess 
import shlex
import utils
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-exp", "--exp", help="experiment name", default="", type=str)
parser.add_argument("-run", "--run", help="run number", default="", type=str)
parser.add_argument("-det", "--det", help="detector alias (e.g. DscCsPad)", default=None, type=str) 
parser.add_argument("-pkTag", "--pkTag", help="tag of cxi file", default="", type=str) 
parser.add_argument("-noe", "--noe", help="number of images", default=-1, type=int)
parser.add_argument("-distance", "--distance", help="distance + or - in mm", default=None, type=str)
parser.add_argument("-pdb", "--pdb", help="pdb", default=None, type=str)
parser.add_argument("-tag", "--tag", help="index tag", default=None, type=str)
parser.add_argument("-geom", "--geom", help="index tag", default=None, type=str)
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
    
rlist = get_run(args.run)

dcenter = None
if args.distance is not None:
    if "#" in args.distance:
        dcenter = int(args.distance.split("#")[0])
        args.distance = args.distance.split("#")[1]
    detectorDistanceList = args.distance.split(',')
else:
    detectorDistanceList = [0]

ps = []
for detectorDistanceString in detectorDistanceList:
    geoM = indexerHelper.GeoFileManager(experimentName=args.exp,runNumber=rlist[0],detectorName=args.det)
    if dcenter is None:
        detectorDistance = geoM.detectorDistance + float(detectorDistanceString) * 1.0e-3
    else:
        detectorDistance = dcenter + float(detectorDistanceString) * 1.0e-3
        
    geoM.changeDistance(detectorDistance, fromfile=args.geom, tag=(args.tag or utils.random_string(N=5)))

    for run in get_run(args.run):
        indH = indexerHelper.IndexHelper(args.exp, run, args.det, outDir = args.outDir)
        indH.pkTag    = args.pkTag
        indH.indexnoe = args.noe 
        indH.pdbfile  = args.pdb 
        indH.tag      = (args.tag or "indexer") + "_" + str("%.4f"%detectorDistance)
        command       = indH.indexCommand(geoM)
        print " #####\n", command, "\n ######"
        process = subprocess.Popen(shlex.split(command))
        ps.append(process)
        
    geoM = None
    indH = None
    """
    Submit without waiting
    """
for p in ps:
    p.communicate()