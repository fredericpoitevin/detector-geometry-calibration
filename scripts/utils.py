"""
1. utils functions
"""
import string
import time
import shlex
import datetime
import psana
import numpy as np 

def getTime():
    """
    return accurate time point in format: Year-Month-Day-Hour:Minute:Second.unique_labels
    """ 
    return datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d-%H:%M:%S.%f')

def getUsername():
    cmd = "whoami"
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    out, err = process.communicate()
    return out

def guessStreamMedian(prior_guess, current):
    """
    haven't implemented this
    """
    return prior_guess
 
def loadPsanaMask(experimentName, runNumber, detectorName):
    ds = psana.DataSource("exp="+experimentName+":run="+str(runNumber)+':idx') 
    det = psana.Detector(detectorName)
    det.do_reshape_2d_to_3d(flag=True)

    run = ds.runs().next()
    times = run.times()
    evt = None
    counter = 0
    while evt is None:
        evt = run.event(times[counter])
        counter += 1
    unassem_img = det.mask(runNumber, calib=True,status=True,edges=True,central=True,unbond=True,unbondnbrs=True)
    assem_img = det.image(evt, unassem_img)
    return unassem_img, assem_img

def latticeVolume(ila, ilb, ilc, ialpha, ibeta, igamma):
    volume = ila*ilb*ilc*np.sqrt(1+2.*np.cos(ialpha)*np.cos(ibeta)*np.cos(igamma)-np.cos(ialpha)**2-np.cos(ibeta)**2-np.cos(igamma)**2)
    return volume



import random 
def random_string(N=20):
    return ''.join([random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(N)])

def date_string():
    return datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d-%H:%M:%S.%f')

