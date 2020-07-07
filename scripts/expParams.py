import numpy as np
import os
import psana

# experiment parameters

def expdet(experimentName,runNumber,detectorName):
    try:
        ds = psana.DataSource("exp="+experimentName+":run="+str(runNumber)+':idx')
    except: 
        return None,None

    run = ds.runs().next()
    env = ds.env()
    times = run.times()
    det = psana.Detector(detectorName)
    epics = ds.env().epicsStore()
    counter = 0
    evt = None
    while evt is None:
        evt = run.event(times[counter])
        counter += 1
        if counter > 1000:
            break
        if counter > len(times)-2:
            break
    return evt,det

class experiparams:

    def __init__(self, experimentName, runNumber, detectorName=None, outDir=None):
        
        self.experimentName = experimentName        # cxic0415  
        self.runNumber = runNumber                  # 98  
        self.detectorName = detectorName            # self.parent.detAlias = self.getDetectorAlias(str(self.parent.detInfo))  
        self.username = os.environ['USER']
        self.paraDir = os.path.dirname(os.path.realpath(__file__))
        self.outDir = outDir 
        
        self.setDefaultPath() 
        


    def setDefaultPath(self):
        if self.outDir is None:
            self.outDir = "/reg/data/ana03/scratch/autosfx/%s/%s"%(self.username,self.experimentName)
        self.outDir = os.path.realpath(self.outDir)
        self.cxiDir = self.outDir+'/r'+str(self.runNumber).zfill(4)
        self.logDir = self.outDir+'/logs/r'+str(self.runNumber).zfill(4)
        self.runDir = self.cxiDir


    def setDefaultPsana(self):
        try: 
            ds = psana.DataSource("exp="+self.experimentName+":run="+str(self.runNumber)+':idx')
        except: 
            raise Exception('!!!!! Invalid experiment name or run number')

        run = ds.runs().next()
        env = ds.env()
        times = run.times()
        det = psana.Detector(self.detectorName)
        epics = ds.env().epicsStore()
        counter = 0
        evt = None
        while evt is None:
            evt = run.event(times[counter])
            counter += 1

        
        self.instrument = det.instrument()        
        from experiment import myExp
        exp = myExp(self.experimentName,self.runNumber,self.detectorName)
        exp.Det 
        self.clen = exp.clen 
        self.clenEpics = exp.clenEpics
                 
        self.detectorDistance = np.mean(det.coords_z(evt))*1.0e-6 
        self.coffset = self.detectorDistance - self.clen 
        self.pixelSize = det.pixel_size(run)*1.0e-6 

