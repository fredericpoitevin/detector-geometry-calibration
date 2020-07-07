from scipy import stats
import numpy as np 
from streamManager import *
import utils as utils

def countIndexNumber(streamfile):
    indexHistogram = getIndexHistogram(streamfile)
    return len(indexHistogram)
    

def getIndexHistogram(streamfile):
    """
    Using stream manager to extract information.
    
    TODO: 
    1. the stream manager may be slow, may need updates
    """
    sm = iStream() 
    sm.initial(streamfile)
    sm.get_label()
    sm.get_info()
    numHits = len(sm.label.hit)
    numIndex = len(sm.label.index)
    indexHistogram = sm.crystal
    indexHistogram[:,9:12] *= 10.
    sm.clear()    
    return numIndex, numHits, indexHistogram


def scoreIndexing(skewness, kurtosis, indexRate=None):
    """
    1. Higher score means better distribution;
    2. Score can be negative;
    
    TODO: 
    1. take numIndex into consideration
    """
    
    score = -999.
    if skewness is None or kurtosis is None:
        return [score]*6  
    score = kurtosis/2. - np.abs(skewness) 
    score = np.sum(score[:3]) + indexRate*40.
    return score 


def evaluateSkewKurt(a,b,c,alpha,beta,gamma):
    
    skewness = [None]*6
    kurtosis = [None]*6
    
    if len(a) < 20:
        return None, None
    
    skewness[0] = stats.skew(a)
    skewness[1] = stats.skew(b)
    skewness[2] = stats.skew(c)
    skewness[3] = stats.skew(alpha)
    skewness[4] = stats.skew(beta)
    skewness[5] = stats.skew(gamma)
    
    kurtosis[0] = stats.kurtosis(a)
    kurtosis[1] = stats.kurtosis(b)
    kurtosis[2] = stats.kurtosis(c)
    kurtosis[3] = stats.kurtosis(alpha)
    kurtosis[4] = stats.kurtosis(beta)
    kurtosis[5] = stats.kurtosis(gamma)
    
    return np.array(skewness), np.array(kurtosis)


def volumeFilter(_lattice):
    """
    Lattice constants can be different, but single-unit-cell volume is the same
    """
    lattice = _lattice.copy()
    (nx,ny) = lattice.shape
    if nx < 20: 
        print "@@@@@ no enough crystals" 
        return [lattice, None]

    Volume = []
    for ii in range(nx):
        singleVolume = utils.latticeVolume(lattice[ii,0].copy(), \
                              lattice[ii,1].copy(), \
                              lattice[ii,2].copy(), \
                              lattice[ii,3]/180.*np.pi, \
                              lattice[ii,4]/180.*np.pi, \
                              lattice[ii,5]/180.*np.pi )
        Volume.append(singleVolume)

    Volume = np.array(Volume)
    # Vmedian = np.nanmedian(V)
    (hist, sampling) = np.histogram(Volume, bins=int(np.amax(Volume)/10000))
    Vcenter = sampling[np.argmax(hist)+1]

    index = np.where((Volume > Vcenter*0.9)*(Volume < Vcenter*1.1) == True)
    if len(index[0]) < 5:
#         print "@@@@@ no enough crystals" 
        return [lattice, None]

    lattice = lattice[index].copy()
#     print '##### volume filtering: ori -> now: ', nx,'->',len(lattice)

    return [lattice, Volume]
    
    

def niggli(unitCell, spacegroup):
    from cctbx import uctbx
    from cctbx import crystal
    uc  =  uctbx.unit_cell( unitCell )      # "51 98 53 89.5 68.3 89.9"
    xs  =  crystal.symmetry(uc, spacegroup) # "P21"
    cbop_prim = xs.change_of_basis_op_to_niggli_cell()
    xs1 = xs.change_basis(cbop_prim)
    a = str(xs1.unit_cell().parameters()).split('(')[-1].split(')')[0].split(',')
    nuc = np.zeros(6,)
    for i in range(6):
        nuc[i] = float(a[i])
    return nuc


def convert2niggli(_lattice):
    lattice = _lattice.copy()
    niggliLattice = lattice.copy()

    spacegroup = "P1"
    for i, val in enumerate(lattice):
        unitCell = ""
        for j in lattice[i,:]:
            unitCell += str(j) + " "
        nuc = niggli(unitCell, spacegroup)
        niggliLattice[i,:] = nuc.copy()
    return niggliLattice


def check90(_lattice):
    lattice = _lattice.copy()
    for idx, each in enumerate(_lattice):
        if np.abs(each[3]-90)<1.5:
            lattice[idx, 3] = 90
        if np.abs(each[4]-90)<1.5:
            lattice[idx, 4] = 90
        if np.abs(each[5]-90)<1.5:
            lattice[idx, 5] = 90
    return lattice


def evaluateIndexing(streamfile, withpdb=True):
    
    numIndex, numHits, indexHistogram = getIndexHistogram(streamfile)
    lattice = indexHistogram[:,9:15].copy()
#     print "##### numHits : ", numHits
#     print "##### numIndex: ", len(lattice)
    if not withpdb:
#         print "##### running niggli and volume filter"
        lattice = check90(lattice)
#         lattice = convert2niggli(lattice)
        [lattice, Volume] = volumeFilter(lattice)

    skewness, kurtosis = evaluateSkewKurt(lattice[:,0], lattice[:,1], lattice[:,2], lattice[:,3], lattice[:,4], lattice[:,5])
#     print "##### skewness: ", None if skewness is None else np.around(skewness,3) 
#     print "##### kurtosis: ", None if kurtosis is None else np.around(kurtosis,3)
    score = scoreIndexing(skewness, kurtosis, indexRate=numIndex*1.0/numHits)
    
    return score
    
    

    
    
