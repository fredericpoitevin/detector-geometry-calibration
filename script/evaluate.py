## return score of a stream file
## 

import numpy as np 
from scipy import stats
from script.streamManager import iStream

class Stream:
    """
    1. get statistics of a stream file
    2. doesn't keep big dataset in memory
    """
    def __init__(self,fstream=None):
        self.fstream = fstream 
        self.load_stream()
        self.outDir = os.path.dirname(self.fstream)

    def load_stream(self):
        sm = iStream() 
        sm.initial(self.fstream)
        sm.get_label()
        sm.get_info()
        import copy
        self.map_label   = copy.deepcopy(sm.label)
        self.map_crystal = copy.deepcopy(sm.crystal)
        self.map_crystal[:,9:12] *= 10.
        sm.clear()

    def numindex(self):
        if self.map_label is None:
            self.load_stream()
        return len(self.map_label.index)

    def numhits(self):
        if self.map_label is None:
            self.load_stream()
        return len(self.map_label.hit)

    def crystal(self):
        if self.map_crystal is None:
            self.load_stream()
        if len(self.map_crystal)==0:
            return None
        return self.map_crystal[:,9:15].copy()

    def skewness(self):
        c = self.crystal()
        if c is None or len(c)<20:
            return None
        
        skewness = [None]*6
        skewness[0] = stats.skew(c[:,0])
        skewness[1] = stats.skew(c[:,1])
        skewness[2] = stats.skew(c[:,2])
        skewness[3] = stats.skew(c[:,3])
        skewness[4] = stats.skew(c[:,4])
        skewness[5] = stats.skew(c[:,5])
        return np.array(skewness)

    def kurtosis(self):
        c = self.crystal()
        if c is None or len(c)<20:
            return None
        
        kurtosis = [None]*6
        kurtosis[0] = stats.kurtosis(c[:,0])
        kurtosis[1] = stats.kurtosis(c[:,1])
        kurtosis[2] = stats.kurtosis(c[:,2])
        kurtosis[3] = stats.kurtosis(c[:,3])
        kurtosis[4] = stats.kurtosis(c[:,4])
        kurtosis[5] = stats.kurtosis(c[:,5])
        return np.array(kurtosis)
    
    def fcrystfel(self):
        with open(fstream,"r") as fr:
            content = []
            start = False;stop=False;
            for line in fr:
                if line.startswith("----- Begin geometry file -----"):
                    start = True;
                elif line.startswith("----- End geometry file -----"):
                    start=False; stop = True
                elif start:
                    content.append(line)
                elif stop:
                    break
        fsave = os.path.join(self.outDir,random_string(12)+".geom")
        with open(fsave,"w") as fw:
            fw.writelines(fsave)
        return fsave

    def fcell(self):
        with open(fstream,"r") as fr:
            content = []
            start = False;stop=False;
            for line in fr:
                if line.startswith("----- Begin unit cell -----"):
                    start = True;
                elif line.startswith("; Please note"):
                    start=False; stop = True
                elif start:
                    content.append(line)
                elif stop:
                    break
        if len(content)<5:
            return None
        fsave = os.path.join(self.outDir,random_string(12)+".geom")
        with open(fsave,"w") as fw:
            fw.writelines(fsave)
        return fsave


class Evaluate:
    def __init__(self,fstreams=[],marker=None):
        self.fstreams=[]
        self.marker = marker or list(range(len(self.fstreams)))
        index = np.argsort(np.array(self.marker))
        self.fstreams = list(np.array(self.fstreams)[index])
        self.marker = list(np.array(self.marker)[index])

    def evaluate(method="standard"):
        scores = []
        for fstream in self.fstreams: 
            score = getattr(self,"evaluate_"+method.lower())(fstream)
            scores.append(score or -999.)
        self.scores = scores
        return self

    def bestream(self):
        scores = self.scores
        if all([i<-900 for i in scores]):
            print("!! Can't find the best geom")
            return None
        index = np.argmax(np.array(scores))
        bestream = self.fstreams[index]
        return Stream(bestream).fcrystfel()

    @staticmethod
    def evaluate_standard(fstream):
        score = -999.
        stm = Stream(fstream)
        skewness = stm.skewness()
        kurtosis = stm.kurtosis()
        indexRate = stm.numindex() * 1.0 / stm.numhits()
        stm = None
        if skewness is None or kurtosis is None:
            return score
        score = kurtosis/2. - np.abs(skewness) 
        score = np.sum(score[:3]) + indexRate*40.
        return score 

