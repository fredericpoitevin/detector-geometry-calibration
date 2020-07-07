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
        if 'cspad2x2' in self.detectorName.lower():
                self.parent.clen = 0.0  
        elif 'cspad' in self.detectorName.lower() and 'cxi' in self.experimentName:
            try:
                self.clenEpics = str(self.detectorName)+'_z'              # detInfo_z
                self.clen = epics.value(self.clenEpics) / 1000.
            except:
                if 'ds1' in self.detectorName.lower():
                    self.clenEpics = str('CXI:DS1:MMS:06.RBV')
                    self.clen = epics.value(self.clenEpics) / 1000.
                elif 'ds2' in self.detectorName.lower():
                    self.clenEpics = str('CXI:DS2:MMS:06.RBV')
                    self.clen = epics.value(self.clenEpics) / 1000.
                else:
                    print "Couldn't handle detector clen."
                    exit()
        elif ('rayonix' in self.detectorName.lower() and 'mfx' in self.experimentName) or \
                 ('cspad' in self.detectorName.lower() and 'mfx' in self.experimentName):
                self.clenEpics =  str('MFX:DET:MMS:04.RBV') #'Rayonix_z'
                try:
                    self.clen = epics.value(self.clenEpics) / 1000.
                except:
                    print "ERROR: No such epics variable, ", self.clenEpics
                    print "ERROR: setting clen to 0.0 metre"
                    self.clen = 0.0  
                 
        self.detectorDistance = np.mean(det.coords_z(evt))*1.0e-6 
        self.coffset = self.detectorDistance - self.clen 
        self.pixelSize = det.pixel_size(run)*1.0e-6 

