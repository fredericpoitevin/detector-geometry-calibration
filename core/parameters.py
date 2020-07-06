import os,sys
import psana
import numpy as np
from core.experiment import Exp


class Path:
    def __init__(self,expName=None,runNumber=None,outDir=None,**kwargs):
        self.expName = expName
        self.runNumber = runNumber 
        self.outDir  = outDir
        self.userName = os.environ.get('USER')
        if self.runNumber is not None:
            self.runNumber = int(self.runNumber)
        self.__dict__.update(kwargs)
        self.set_default_path()
        
    def set_default_path(self):
        self.runDir  = None
        self.dataDir = None
        self.fgeom   = None
        self.smask   = None
        self.pmask   = None
        if self.outDir is not None:
            self.outDir = os.path.realpath(self.outDir)
        if (self.expName is None) or (self.runNumber is None):
            return 
        if self.outDir is None or not os.path.isdir(self.outDir):
            self.outDir = '/reg/data/ana03/scratch/autosfx/%s/%s'%(self.userName,self.expName)
        self.outDir = os.path.realpath(self.outDir)
        self.runDir = os.apth.join(self.outDir,"r%.4d"%int(self.runNumber))
        self.dataDir = "/reg/d/psdm/%s/%s"%(self.expName[:3],self.expName)
        self.fgeom = os.path.join(self.runDir,".temp.geom")
        self.smask = os.path.join(self.runDir,"staticMask.h5")
        self.pmask = os.path.join(self.runDir,"psanaMask.npy")

    def dir_make(self):
        if self.outDir is None:
            return 
        if not os.path.isdir(self.outDir):
            os.makedirs(self.outDir)

        if self.runDir is None:
            return 
        if not os.path.isdir(self.runDir):
            os.makedirs(self.runDir)

