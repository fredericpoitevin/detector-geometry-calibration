import psana
import numpy as np
import h5py
import os
from expParams import experiparams
 

def checkStartFiles(experimentName, runNumber):
    copyParams = experiparams(experimentName=experimentName, runNumber=runNumber)
    cxiDir = copyParams.cxiDir

    status = True
    if cxiDir is None or not os.path.exists(cxiDir):
        print "@@@@@ cxiDir does not exist "
        status = False
    if not os.path.isfile(cxiDir+'/staticMask.h5'):
        print "@@@@@ statisMask.h5 is missing "
        status = False
    if not os.path.isfile(cxiDir + '/psanaMask.npy'):
        print "@@@@@ psanaMask.npy is missing "
        status = False
    if not os.path.isfile(cxiDir+"/.temp.geom"):
        print "@@@@@ .temp.geom is missing "
        status = False
    return status


def loadPsanaMask(experimentName, runNumber, detectorName):
    ds = psana.DataSource("exp="+experimentName+":run="+str(runNumber)+':idx') 
    det = psana.Detector(detectorName)
    det.do_reshape_2d_to_3d(flag=True)

    run = ds.runs().next()
    times = run.times()
    evt = None
    counter = 0
    while evt is None:
        evt = run.event(times[counter])
        counter += 1
    unassem_img = det.mask(runNumber, calib=True,status=True,edges=True,central=True,unbond=True,unbondnbrs=True)
    assem_img = det.image(evt, unassem_img)
    return unassem_img, assem_img


# Save static mask in cheetah format, which is the "staticMask.h5" file
def saveCheetahStaticMask(unassem_img, experimentName, detectorName, fsave):
    # Save cheetah format mask

    if 'cspad' in detectorName.lower() and 'cxi' in experimentName:
        dim0 = 8 * 185
        dim1 = 4 * 388
    elif 'rayonix' in detectorName.lower() and 'mfx' in experimentName:
        dim0 = 1920
        dim1 = 1920
    elif 'rayonix' in detectorName.lower() and 'xpp' in experimentName:
        dim0 = 1920
        dim1 = 1920
    else:
        print "saveCheetahFormatMask not implemented"

    print "Saving static mask in Cheetah format: ", fsave
    myHdf5 = h5py.File(fsave, 'w')
    dset = myHdf5.create_dataset('/entry_1/data_1/mask', (dim0, dim1), dtype='int')

    # Convert calib image to cheetah image
    if True:
        img = np.zeros((dim0, dim1))
        counter = 0
        if 'cspad' in detectorName.lower() and 'cxi' in experimentName:
            for quad in range(4):
                for seg in range(8):
                    img[seg * 185:(seg + 1) * 185, quad * 388:(quad + 1) * 388] = unassem_img[counter, :, :]
                    counter += 1
        elif 'rayonix' in detectorName.lower() and 'mfx' in experimentName:
            img = unassem_img[:, :]  # psana format
        elif 'rayonix' in detectorName.lower() and 'xpp' in experimentName:
            img = unassem_img[counter, :, :]  # psana format

    dset[:, :] = img
    myHdf5.close()


# Get the geometry file position
import Detector.PyDetector
import PSCalib.GlobalUtils as gu

def findPsanaGeometry(experimentName, runNumber, detectorName):

    ds = psana.DataSource("exp="+experimentName+":run="+str(runNumber)+':idx')
    det = psana.Detector(detectorName)
    det.do_reshape_2d_to_3d(flag=True)

    run = ds.runs().next()
    times = run.times()
    evt = None
    counter = 0
    while evt is None:
        evt = run.event(times[counter])
        counter += 1

    source = Detector.PyDetector.map_alias_to_source(detectorName, ds.env())  # 'DetInfo(CxiDs2.0:Cspad.0)'
    calibSource = source.split('(')[-1].split(')')[0]  # 'CxiDs2.0:Cspad.0'
    detectorType = gu.det_type_from_source(source)  # 1
    calibGroup = gu.dic_det_type_to_calib_group[detectorType]  # 'CsPad::CalibV1'
    detectorName = gu.dic_det_type_to_name[detectorType].upper()  # 'CSPAD'

    calibPath = "/reg/d/psdm/" + experimentName[0:3] + \
                         "/" + experimentName + "/calib/" + \
                         calibGroup + "/" + calibSource + "/geometry/"

    # Determine which calib file to use
    geometryFiles = os.listdir(calibPath)
    print "geometry: \n " + "\n".join(geometryFiles) 
    calibFile = None
    minDiff = -1e6
    for fname in geometryFiles:
        if fname.endswith('.data'):
            endValid = False
            startNum = int(fname.split('-')[0])
            endNum = fname.split('-')[-1].split('.data')[0]
            diff = startNum - runNumber
            # Make sure it's end number is valid too
            if 'end' in endNum:
                endValid = True
            else:
                try:
                    if runNumber <= int(endNum):
                        endValid = True
                except:
                    continue
            if diff <= 0 and diff > minDiff and endValid is True:
                minDiff = diff
                calibFile = calibPath + fname

    return calibFile


def CalibFileToGeomFile(calibFile, detectorName, fsave):
    # Read the geometry file and save it to temp.geom file in the setup folder
    from psgeom import camera
    if 'cspad' in detectorName.lower():
        geom = camera.Cspad.from_psana_file(calibFile)
        geom.to_crystfel_file(fsave)
    elif 'rayonix' in detectorName.lower():
        geom = camera.CompoundAreaCamera.from_psana_file(calibFile)
        geom.to_crystfel_file(fsave)
    return True


def setupNewRun(experimentName=None, runNumber=None, detectorName=None, outDir = None, copyRun=None):

    params = experiparams(experimentName=experimentName, runNumber=runNumber, detectorName=detectorName, outDir=outDir)
    copyParams = experiparams(experimentName=experimentName, runNumber=copyRun, detectorName=detectorName, outDir = outDir)
    if not os.path.isdir(params.cxiDir):
        print params.cxiDir
        os.makedirs(params.cxiDir)

    if copyRun is not None:
        status = checkStartFiles(experimentName, copyRun)
        if status:
            from shutil import copyfile
            copyfile(src=copyParams.cxiDir+'/staticMask.h5', dst=params.cxiDir+'/staticMask.h5')
            copyfile(src=copyParams.cxiDir+'/psanaMask.npy', dst=params.cxiDir+'/psanaMask.npy')
            copyfile(src=copyParams.cxiDir+"/.temp.geom", dst=params.cxiDir+"/.temp.geom")
            copyfile(src=copyParams.cxiDir+"/.temp.geom", dst=params.cxiDir+"/temp.geom")
            print "##### copy file from run %d to %d" % (copyRun, runNumber)
            return True

    # get the psana mask from the psana server
    unassem_img, assem_img = loadPsanaMask(experimentName, runNumber, detectorName)
    np.save(params.cxiDir+'/psanaMask.npy', assem_img)
    print "##### save psanaMask: ", params.cxiDir+'/psanaMask.npy'

    ## save unassem_img to cheetah mask
    saveCheetahStaticMask(unassem_img, experimentName, detectorName, params.cxiDir+'/staticMask.h5')
    print "##### save cheetah mask: ", params.cxiDir+'/staticMask.h5'

    ## load psana geometry
    calibFile = findPsanaGeometry(experimentName, runNumber, detectorName)
    print "##### load calibFile: ", calibFile

    ############################
    # Sometimes the geom file is not compatible with psocake, we need to modify a little bit
    fgeom = params.cxiDir+"/temp.geom"
    CalibFileToGeomFile(calibFile, detectorName, fgeom)
    print "##### convert calibFile to geometry file"

    ## load geom file and make a copy to .temp.geom
    f = open(fgeom)
    lines = f.readlines()
    f.close()

    f = open(params.cxiDir+"/.temp.geom",'w')
    params.setDefaultPsana()

    for i in lines:
        #if 'mask' in i:
        #    f1.write(';'+i)
        if 'clen' in i:
            f.write(i.split(';')[-1])
        elif 'coffset' in i:
            f.write(i.split('=')[0]+"= "+str(params.coffset)+'\n') 
        else:
            f.write(i)
    f.close()

    return True
