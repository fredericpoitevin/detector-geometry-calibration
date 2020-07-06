

class Setup:
    ## action 
    def __init__(self):
        pass 
    def set(self):
        return 
    def refresh(self):
        return 
    def start(self):
        return 

class Peakf:
    ## action
    def __init__(self,expName=None,runNumber=None,detName=None,outDir=None,exp=None,path=None):
        self.exp  = exp  or myExp(expName,runNumber,detName)
        self.path = path or myPath(expName,runNumber,outDir)

class Index:
    ## action
    def __init__(self):
        pass 

class Merge:
    ## action
    def __init__(self):
        pass 

class Powder:
    ## action
    def __init__(self):
        pass 

class Center:
    ## action
    def __init__(self):
        pass

class Distz:
    def __init__(self):
        pass 
    def optimize(self):
        return 
    def 

class Geom:
    def __init__(self):
        pass 
    def deploy(self,center=None,distance=None,fcrystfel=None):
        return 

class Group:
    def __init__(self,runList=None,expName=None,detName=None,outDir=None):
        self.expName = expName 
        self.detName = detName 
        self.outDir  = outDir  
        self.runList = self.runs(runList) 

    def runs(self,mark=None):
        if isinstance(mark,(int,long)):
            return [mark]
        if isinstance(mark,(list,tuple,set)):
            return list(mark)
        if not isinstance(mark,str):
            return []
        runList = []
        for runs in mark.split(","):
            runs_strip = runs.rstrip().lstrip()
            if runs_strip == "":
                continue
            if "-" in runs_strip:
                start,stop = runs_strip.split("-")
                runList.extend(range(int(start),int(stop)+1))
            runList.append(int(runs_strip))
        return sorted(runList)

    def set(self,**kwargs):
        self.runList = self.runs(mark)

    def setup(self):
        return 
    def powder(self):
        return 
    def peakf(self):
        return 
    def index(self):
        return 
    def merge(self):
        return 

class Run:
    def __init__(self,runNumber=None,expName=None,detName=None,outDir=None,exp=None,path=None):
        self.exp  = exp  or myExp(expName,runNumber,detName)
        self.path = path or myPath(expName,runNumber,outDir)
        self.params = {}

    def set(self,runNumber=None,expName=None,detName=None,outDir=None):
        self.exp  = myExp(  expName or self.expName, \
                            runNumber or self.runNumber, \
                            detName or self.detName)
        self.path = myPath( expName or self.expName, \
                            runNumber or self.runNumber, \
                            outDir or self.outDir)
        return self
    
    def setup(self,**kwargs):
        params = {}
        p = Setup(exp=self.exp,path=self.path).set(**kwargs)
        if p.start():
            params["status"] = "done"
        else:
            params["status"] = "failed"
        self.
        return self

    def powder(self,**kwargs):
        if not hasattr(self,"status_setup"):
            self.setup()
        if self.status_setup:
            if Powder(exp=self.exp,path=self.path).set(**kwargs).launch():
                self.status_powder = True
            else:
                self.status_powder = False
        else:
            print "!! Can't setup the experiment"
        return self

    def peakf(self,**kwargs):
        if not hasattr(self,"status_setup"):
            self.setup()
        if self.status_setup:
            if Peakf(exp=self.exp,path=self.path).set(**kwargs).launch():
                self.status_peakf = True
            else:
                self.status_peakf = False
        else:
            print "!! Can't setup the experiment"
        return self

    def index(self,**kwargs):
        if not hasattr(self,"status_setup"):
            self.setup()
        if not hasattr(self,"status_peakf"):
            self.peakf()
        if self.status_setup and self.status_peakf:
            if Powder(exp=self.exp,path=self.path).set(**kwargs).launch():
                self.status_powder = True
            else:
                self.status_powder = False
        else:
            print "!! Can't setup the experiment"
        return self

class myManager:
    def __init__(self,expName=None,detName=None,outDir=None,runNumber=None,**kwargs):
        self.group = Group(expName,detName,outDir,**kwargs)
        self.run   = Run(expName,detName,outDir)
        self.merge = Merge(expName,outDir)