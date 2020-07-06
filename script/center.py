import os,sys
import numpy as np


class Center:
    def __init__(self):
        pass  

    @staticmethod
    def powder_optimize(_powderImg, _mask=None, logarithm=False, guessRow=None, guessCol=None,_range=100):
        """
        return the center in pixel value
        """
        if _mask is not None:
            mask = _mask.copy() * (_powderImg>0)
        else:
            mask = (_powderImg>0).astype(int)
        powderImg = _powderImg * mask
     
        matrixCx_px = (powderImg.shape[0]-1.)/2.
        matrixCy_px = (powderImg.shape[1]-1.)/2.
        print("Square center: ", matrixCx_px, matrixCy_px)

        if logarithm:
            index_up = np.where(powderImg>1)
            index_do = np.where(powderImg<=1)
            powderImg[index_up] = np.log(powderImg[index_up])

            mask[index_do] = 0 
            powderImg *= mask

        weightCx_px, weightCy_px = Center.weightedCenter(powderImg * mask)
        print("Weight centre: ", weightCx_px, weightCy_px)

        if not guessRow:
            guessRow = weightCx_px
        if not guessCol:
            guessCol = weightCy_px
        
        optimalCx_px, optimalCy_py = Center.findDetectorCentre(powderImg,guessRow=guessRow,guessCol=guessCol,_range=_range)
        print("Optimum center along row,centre along column: ", optimalCx_px, optimalCy_py)
        
        return (optimalCx_px, optimalCy_py)

    @staticmethod
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

    @staticmethod
    def findDetectorCentre(I, guessRow=None, guessCol=None, _range=50):
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
            A,B = Center.getTwoHalves(I,centreCol,axis=0)
            scoreCol[i] = Center.getCorr(A,B)
        centreCol = searchArray[np.argmax(scoreCol)] 

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
            A,B = Center.getTwoHalves(I,centreRow,axis=1)
            scoreRow[i] = Center.getCorr(A,B)
        centreRow = searchArray[np.argmax(scoreRow)] 

        return centreCol, centreRow


    @staticmethod
    def getTwoHalves(I,centre,axis=None):
        # Return two equal sized halves of the input image
        # If axis is None, halve along the first axis
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

    @staticmethod
    def getScore(A,B):
        ind = (A>0) & (B>0)
        dist = sd.euclidean(A[ind].ravel(),B[ind].ravel())
        numPix = len(ind[np.where(ind==True)])
        return dist/numPix

    @staticmethod
    def getCorr(A,B):
        ind = (A>0) & (B>0)
        if np.sum(ind)<=20:
            return -1
        dist = np.corrcoef(A[ind].ravel(),B[ind].ravel())[0,1]
        return dist

    @staticmethod
    def deploy_calib():
        return 

    @staticmethod
    def deploy_geom():
        return 