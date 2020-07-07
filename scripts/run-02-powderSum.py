import psana
import os,sys
import numpy as np
from mpidata import mpidata
import utils as utils
from expParams import experiparams

from mpi4py import MPI
comm = MPI.COMM_WORLD
comm_rank = comm.Get_rank() 
comm_size = comm.Get_size()
assert comm_size>1, 'At least 2 MPI ranks required'


import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-exp", "--exp", help="experiment name", default=None, type=str)
parser.add_argument("-run", "--run", help="run number", default=None, type=int)
parser.add_argument("-noe", "--noe", help="number of images", default=3000, type=int)
parser.add_argument("-det", "--det", help="detector alias (e.g. DscCsPad)", default=None, type=str)
parser.add_argument("-outDir", "--outDir", help="", default="./", type=str)
args = parser.parse_args()

if args.det is None:
    from experiment import myExp
    runs = [args.run]
    exp = myExp(args.exp,runs[0])
    try: exp.Det
    except: pass 
    args.det = exp.detName
    print args.det 
    
def runmaster(args):

    exprun = "exp="+str(args.exp)+":run="+str(args.run)
    
    ds = psana.DataSource(exprun+':idx')
    run = ds.runs().next()
    det = psana.Detector(args.det)
    times = run.times()
    
    evt = None
    counter = 0
    while evt is None:
        evt = run.event(times[counter]) 
        counter += 1

    max_img = None
    mean_img = None
    median_img = None 

    ## counter is a monitor to record how many images have been process in total
    ## nClients is the number of clients to process the data
    counter = 0.
    nClients = comm_size-1
    while nClients > 0:
        # Remove client if the run ended
        md = mpidata()
        md.recv()

        if max_img is None:
            max_img = md.max_img
            mean_img = md.mean_img
            median_img = md.median_img 
        else:
            max_img = np.maximum(max_img, md.max_img)
            mean_img = (mean_img * counter + md.mean_img * md.small.counter)*1.0/(counter + md.small.counter)

        counter = counter + md.small.counter
        nClients -= 1
    
    print "##### Total number of images: %s/%s " % (str(counter), str(args.noe))
    params = experiparams(experimentName=args.exp, runNumber=args.run, outDir=os.path.realpath(args.outDir))
    np.save(params.cxiDir+"/"+args.exp+"_"+str(args.run).zfill(4)+"_"+str(args.det)+"_max_assem.npy", det.image(evt, max_img))
    np.save(params.cxiDir+"/"+args.exp+"_"+str(args.run).zfill(4)+"_"+str(args.det)+"_max.npy", max_img)
    np.save(params.cxiDir+"/"+args.exp+"_"+str(args.run).zfill(4)+"_"+str(args.det)+"_mean_assem.npy", det.image(evt, mean_img/counter))
    np.save(params.cxiDir+"/"+args.exp+"_"+str(args.run).zfill(4)+"_"+str(args.det)+"_mean.npy", mean_img/counter)
    print "## saving the average powder pattern to: %s" % params.cxiDir



def runclient(args):
    ## "exprun" has the format: "(e.g. exp=xppd7114:run=43)"
    exprun = "exp="+str(args.exp)+":run="+str(args.run)

    ds = psana.DataSource(exprun+':idx')
    run = ds.runs().next()
    det = psana.Detector(args.det)
    times = run.times()
    eventTotal = len(times)

    if args.noe == -1: 
        args.noe = eventTotal
    else:
        args.noe = min(eventTotal, args.noe)

    max_img = None
    mean_img = None
    median_img = None
    square_img = None

    counter = 0
    nClients = comm_size-1
    for nevent in range(args.noe):
        if nevent >= eventTotal: 
            break
        if nevent%nClients != comm_rank-1: 
            continue

        evt = run.event(times[nevent])
        img = det.calib(evt)

        if img is None: 
            continue
        if max_img is None:
            max_img = img
            mean_img = img
            median_img = img 
        else:
            max_img = np.maximum(max_img, img)
            mean_img = (mean_img * counter + img)*1.0/(counter+1)
            median_img = utils.guessStreamMedian(median_img, img) 
        counter += 1

        print "##### Rank %3d is processing event %3d/%d" % (comm_rank, nevent, args.noe)
            
    print "##### Rank %3d processed %3d/%d" % (comm_rank, counter, args.noe)
    md=mpidata()
    md.addarray('max_img', max_img)      
    md.addarray('mean_img', mean_img) 
    md.addarray('median_img', median_img) 
    md.small.counter = counter
    md.send()


if comm_rank==0: 
    runmaster(args) 
else:  
    runclient(args) 

MPI.Finalize()