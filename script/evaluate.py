## return score of a stream file
## 

class Stream:
    """
    1. get statistics of a stream file
    2. doesn't keep big dataset in memory
    """
    def __init__(self,fstream=None):
        self.fstream = fstream
    def numindex(self):
        return 
    def numhits(self):
        return 
    def crystals(self):
        return 
    def skewness(self):
        return 
    def kortours(self):
        return 
    def funitcell(self):
        return 
    def withcell(self):
        return True



class Evaluate:
    def __init__(self,fstreams=[],marker=None):
        self.fstreams=[]
    def evaluate(method="standard"):
        scores = getattr(self,"evaluate_"+method.lower())()
         

    def evaluate_standard(marker,fstreams):
        return 
    def evaluate_numindex(marker,fstreams):
        return 
    def evaluate_distri(marker,fstreams):
        return 