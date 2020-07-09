import numpy as np
import scipy.spatial.distance as sd
from PSCalib.CalibFileFinder import deploy_calib_file
import psana
from expParams import experiparams


# guess center by summing up all pixels
def weightedCenter(I):
    nx, ny = I.shape
    xaxis = np.arange(nx)
    yaxis = np.arange(ny)
    (x,y) = np.meshgrid(xaxis, yaxis, indexing='ij')
    cx = np.sum(x*I)/np.sum(I)
    cy = np.sum(y*I)/np.sum(I)
    cx = int(round(cx))
    cy = int(round(cy))
    return (cx,cy)

def findDetectorCentre(I, guessRow=None, guessCol=None, _range=0):
    """
    :param I: assembled image
    :param guessRow: best guess for centre row position (optional)
    :param guessCol: best guess for centre col position (optional)
    :param range: range of pixels to search either side of the current guess of the centre
    :return:
    """
    _range = int(_range)
    # Search for optimum column centre
    if guessCol is None:
        startCol = 1 # search everything
        endCol = I.shape[1]
    else:
        startCol = guessCol - _range
        if startCol < 1: startCol = 1
        endCol = guessCol + _range
        if endCol > I.shape[1]: endCol = I.shape[1]
    searchArray = np.arange(startCol,endCol)
    scoreCol = np.zeros(searchArray.shape)
    for i, centreCol in enumerate(searchArray):
        A,B = getTwoHalves(I,centreCol,axis=0)
        scoreCol[i] = getCorr(A,B)
    centreCol = searchArray[np.argmin(scoreCol)]
    if True:
#         pass
        import matplotlib.pyplot as plt
        plt.plot(searchArray, scoreCol,'x-')
        plt.title(str(centreCol))
        plt.show()

    # Search for optimum row centre
    if guessRow is None:
        startRow = 1 # search everything
        endRow = I.shape[0]
    else:
        startRow = guessRow - _range
        if startRow < 1: startRow = 1
        endRow = guessRow + _range
        if endRow > I.shape[0]: endRow = I.shape[0]
    searchArray = np.arange(startRow,endRow)
    scoreRow = np.zeros(searchArray.shape)
    for i, centreRow in enumerate(searchArray):
        A,B = getTwoHalves(I,centreRow,axis=1)
        scoreRow[i] = getCorr(A,B)
    centreRow = searchArray[np.argmin(scoreRow)]
    if True:
        plt.plot(searchArray, scoreRow,'x-')
        plt.title(str(centreRow))
        plt.show()

    return centreCol, centreRow


# Return two equal sized halves of the input image
# If axis is None, halve along the first axis
def getTwoHalves(I,centre,axis=None):
    if axis is None or axis == 0:
        A = I[:centre,:].copy()
        B = np.flipud(I[centre:,:].copy())

        (numRowUpper,_) = A.shape
        (numRowLower,_) = B.shape
        if numRowUpper >= numRowLower:
            numRow = numRowLower
            A = A[-numRow:,:].copy()
        else:
            numRow = numRowUpper
            B = B[-numRow:,:].copy()
    else:
        A = I[:,:centre].copy()
        B = np.fliplr(I[:,centre:].copy())

        (_,numColLeft) = A.shape
        (_,numColRight) = B.shape
        if numColLeft >= numColRight:
            numCol = numColRight
            A = A[:,-numCol:].copy()
        else:
            numCol = numColLeft
            B = B[:,-numCol:].copy()
    return A, B


def getScore(A,B):
    ind = (A>0) & (B>0)
    dist = sd.euclidean(A[ind].ravel(),B[ind].ravel())
    numPix = len(ind[np.where(ind==True)])
    return dist/numPix


def getCorr(A,B):
    ind = (A>0) & (B>0)
    dist = 1 - np.corrcoef(A[ind].ravel(),B[ind].ravel())[0,1]
    return dist


def psanaCenter(experimentName, runNumber, detectorName):
    """
    load current center from psana
    """
    ds = psana.DataSource("exp="+experimentName+":run="+str(runNumber)+':idx')
    run = ds.runs().next()
    det = psana.Detector(detectorName)
    times = run.times()
    evt = None
    counter = 0
    while evt is None:
        evt = run.event(times[counter]) # guarantee we have a valid event
        counter += 1
    psanaCx, psanaCy = det.point_indexes(evt, pxy_um=(0, 0))
    pixelSize = det.pixel_size(evt)
    print("Current centre along row,centre along column: ", psanaCx, psanaCy)
    return psanaCx, psanaCy


def findCenterPowderSum(_powderImg, _mask=None):
    """
    optimize the center with the powderSum pattern
    """
    if _mask is not None:
        powderImg = _powderImg * _mask
 
    matrixCx = (powderImg.shape[0]-1.)/2.
    matrixCy = (powderImg.shape[1]-1.)/2.
    print("Matrix center: ", matrixCx, matrixCy)

    guessCx, guessCy = weightedCenter(powderImg)
    print("Guess centre: ", guessCx, guessCy)

#     index = np.where(powderImg>0)
#     powderImg[index] = np.log(powderImg[index])
    
    optimalCx, optimalCy = findDetectorCentre(powderImg, guessCx, guessCy, _range=100)
    print("Optimum centre along row,centre along column: ", optimalCx, optimalCy)
    
    return (optimalCx, optimalCy)


def findCenterSilverBehenate(_silverBehenateImage, _pixelSize, _waveLength, _mask=None):
    """
    _silverBehenateImage: diffraction pattern of silver Behenate
    _pixelSize: in meter
    _waveLength: in meter
    # estimate distance and center
    """
    return (optimalCx, optimalCy, optimalCz)


def deployCenter(experimentName, runNumber, detectorName, newCx, newCy):
    ## deploy the new geometry file
    ## Calculate detector translation in x and y
    ds = psana.DataSource("exp="+experimentName+":run="+str(runNumber)+':idx')
    run = ds.runs().next()
    det = psana.Detector(detectorName)
    times = run.times()
    evt = None
    counter = 0
    while evt is None:
        evt = run.event(times[counter]) # guarantee we have a valid event
        counter += 1
    psanaCx, psanaCy = det.point_indexes(evt, pxy_um=(0, 0))
    pixelSize = det.pixel_size(evt)

    print "##### current psana center: ", psanaCx, psanaCy

    dx = pixelSize * (psanaCx - newCx)  # microns
    dy = pixelSize  * (psanaCy - newCy)  # microns
    geo = det.geometry(evt)

    if 'cspad' in detectorName.lower() and 'cxi' in experimentName:
        geo.move_geo('CSPAD:V1', 0, dx=dx, dy=dy, dz=0)
    elif 'rayonix' in detectorName.lower() and 'mfx' in experimentName:
        top = geo.get_top_geo()
        children = top.get_list_of_children()[0]
        geo.move_geo(children.oname, 0, dx=dx, dy=dy, dz=0)
    elif 'rayonix' in detectorName.lower() and 'xpp' in experimentName:
        top = geo.get_top_geo()
        children = top.get_list_of_children()[0]
        geo.move_geo(children.oname, 0, dx=dx, dy=dy, dz=0)
    else:
        print "autoDeploy not implemented"

    params = experiparams(experimentName=experimentName, runNumber=runNumber, detectorName=detectorName)
    fname = params.cxiDir + "/" + str(runNumber) + '-end.data'
    print "fname: ", fname
    geo.save_pars_in_file(fname)
    print "#################################################"
    print "Deploying psana detector geometry: ", fname
    print "#################################################"
    cmts = {'exp': experimentName, 'app': 'psocake', 'comment': 'auto recentred geometry'}
    calibDir = '/reg/d/psdm/' + experimentName[:3] + '/' + experimentName +  '/calib'
    deploy_calib_file(cdir=calibDir, src=str(det.name), type='geometry', run_start=int(runNumber), run_end=None, ifname=fname, dcmts=cmts, pbits=0)

