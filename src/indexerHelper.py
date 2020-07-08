import numpy as np 
import copy 
from expParams import experiparams
import os
import utils
 

def indexCommand(experimentName=None, runNumber=None, detectorName=None, geomfile=None, outDir=None, \
                 queue=None, pixelSize=None, instrument=None, coffset=None, clenEpics=None, \
                 peakMethod='cxi', intRadius='3,4,5', indexingMethod='mosflm,dirax', minPeaks=15, \
                 maxPeaks=2048, minRes=-1, tolerance='5,5,5,1.5', tag="", pkTag="", \
                 indexsample='crystal', chunkSize=200, indexnoe=-1, logger='False', \
                 keepData='True', likelihood=0, pdbfile=None):

    command = "indexCrystals" + \
            " -e " + experimentName + \
            " -d " + detectorName + \
            " --geom " + geomfile + \
            " --peakMethod " + peakMethod + \
            " --integrationRadius " + intRadius + \
            " --indexingMethod " + indexingMethod + \
            " --minPeaks " + str(minPeaks) + \
            " --maxPeaks " + str(maxPeaks) + \
            " --minRes " + str(minRes) + \
            " --tolerance " + str(tolerance) + \
            " --outDir " + str(outDir) + \
            " --sample " + indexsample + \
            " --queue " + queue + \
            " --chunkSize " + str(chunkSize) + \
            " --noe " + str(indexnoe) + \
            " --instrument " + instrument + \
            " --pixelSize " + str(pixelSize) + \
            " --coffset " + str(coffset) + \
            " --clenEpics " + clenEpics + \
            " --logger " + str(logger) + \
            " --keepData " + str(keepData) + \
            " --likelihood " + str(likelihood)

    if tag is not None and tag != "":
        command += " --tag " + str(tag)
    if pkTag is not None and pkTag != "":
        command += " --pkTag " + str(pkTag)
    if pdbfile is not None and os.path.isfile(pdbfile): 
        command += " --pdb " + pdbfile

    command += " --run " + str(runNumber)

    return command


class GeoFileManager:

    def __init__(self, experimentName=None,runNumber=None,detectorName=None):
        self.experimentName = experimentName
        self.runNumber = runNumber
        self.detectorName = detectorName
        self.loadPsanaGeo()

    def loadPsanaGeo(self):
        self.params = experiparams(self.experimentName, self.runNumber, detectorName=self.detectorName)
        self.params.setDefaultPsana() 
        self.detectorDistance = self.params.detectorDistance
        self.coffset = self.params.coffset
        self.clen = self.params.clen 
        self.geomfile = self.params.cxiDir + "/.temp.geom"

    def changeCenter(self, fromfile=None, newCenter=None, tofile=None):
        if tofile is None:
            tofile = self.input + "-newCenter-"+str(newCenter)
        return True
        
    def changeCoffset(self, newCoffset, fromfile=None, tofile=None, tag=None):

        if fromfile is None:
            fromfile = self.params.cxiDir + "/.temp.geom"
        if tofile is None:
            tofile = fromfile + "-newCoffset-" + str(newCoffset)
            if tag is not None:
                tofile += "-" + str(tag)
            
        f = open(fromfile, 'r')
        content = f.readlines()
        f.close()

        f = open(tofile, 'w')
        for i, val in enumerate(content):
            if 'coffset =' in val: 
                content[i] = val.split('=')[0]+"= "+str(newCoffset)+'\n'
        f.writelines(content)
        f.close()

        self.geomfile = tofile 

        print "##### old geom: ", fromfile
        print "##### old params: distance=%f / coffset=%f / clen=%f"%(self.detectorDistance, self.coffset, self.clen) 

        self.coffset = newCoffset
        self.detectorDistance = self.coffset + self.clen 

        print "##### new geom: ", tofile
        print "##### new params: distance=%f / coffset=%f / clen=%f"%(self.detectorDistance, self.coffset, self.clen) 

        return tofile

    def changeDistance(self, newDistance, fromfile=None, tofile=None, tag=None):

        if fromfile is None:
            fromfile = self.params.cxiDir + "/.temp.geom"
        if tofile is None:
            tofile = fromfile + "-newDistance-"+str(newDistance) 
            if tag is not None:
                tofile += "-" + str(tag)

        print "##### old geom: ", fromfile
        print "##### old params: distance=%f / coffset=%f / clen=%f"%(self.detectorDistance, self.coffset, self.clen) 

        self.detectorDistance = newDistance
        self.coffset = self.detectorDistance - self.clen 

        f = open(fromfile, 'r')
        content = f.readlines()
        f.close()

        if not os.path.isfile(tofile):
            f = open(tofile, 'w')
            for i, val in enumerate(content):
                if 'coffset =' in val: 
                    content[i] = val.split('=')[0]+"= "+str(self.coffset)+'\n'
            f.writelines(content)
            f.close()

        self.geomfile = tofile 

        print "##### new geom: ", tofile
        print "##### new params: distance=%f / coffset=%f / clen=%f"%(self.detectorDistance, self.coffset, self.clen) 

        return tofile


class IndexHelper:

    def __init__(self, experimentName, runNumber, detectorName, outDir=None):
        self.experimentName = experimentName
        self.runNumber = runNumber
        self.detectorName = detectorName 
        self.outDir = outDir
        self.setDefaultParams()
        
    def setDefaultParams(self):
        params = experiparams(self.experimentName, self.runNumber, detectorName=self.detectorName, outDir=self.outDir)
        params.setDefaultPsana()
        
        self.queue = 'psanaq' 
        ### TODO: psocake accept former directory as outDir
        self.outDir = params.outDir
        ### TODO: indexnoe is actually not implemented in psocake
        self.indexnoe = -1
        self.pkTag = ""
        self.instrument = params.instrument
        self.pixelSize = params.pixelSize 
        self.pdbfile = None
        self.clenEpics = params.clenEpics
        self.likelihood = 0.
        self.tag = "index-"+utils.getTime()

    def indexCommand(self, geoManager):
        
        cmd = indexCommand(experimentName=self.experimentName, runNumber=self.runNumber, \
                           detectorName=self.detectorName, geomfile=geoManager.geomfile, \
                           outDir=self.outDir, queue=self.queue, pixelSize=self.pixelSize, likelihood=self.likelihood, \
                           instrument=self.instrument, coffset=geoManager.coffset, clenEpics=self.clenEpics, \
                           tag=self.tag, pkTag = self.pkTag, pdbfile=self.pdbfile, indexnoe=self.indexnoe)
        
        return cmd 
        

