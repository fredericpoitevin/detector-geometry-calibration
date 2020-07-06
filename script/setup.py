import numpy as np
import os,sys
from core.experiment import Exp
from core.params import Path

"""
1. setup directory for an experiment/run
    - path_ready, path_create
2. load geometry of an experiment
    - geom_ready, geom_create
3. check whether data is available
    - xtc_ready, xtc_on
4. calib
    - calib_ready, calib_create
5. psaan mask
    - pmask_ready, pmask_make
6. static mask
    - smask_ready, smask_make
"""

class Setup(Path):
    def __init__(self,expName=None,runNumber=None,detName=None,outDir=None):
        super(myPath,self).__init__(expName,runNumber,detName,outDir)
        self.exp = myExp(expName,runNumber,detName)
        try: self.exp.Det
        except: pass 

    ## all 
    def run_ready(self):
        if self.expName is None or self.runNumber is None:
            return -1
        if not self.xtc_on():
            return -1
        if not self.xtc_ready():
            return -1
        if not self.calib_ready():
            return -1
        if not self.path_ready():
            return 0
        if not self.geom_ready():
            return 0
        if not self.pmask_ready():
            return 0
        if not self.smask_ready():
            return 0
        return 1

    def run_make(self):
        ready = self.run_ready()
        if ready == -1:
            return False
        elif ready == 1:
            return True
        ## not ready
        if not self.path_ready():
            success = success and self.path_make()
        if not self.geom_ready():
            self.geom_make()
        if not self.pmask_ready():
            self.pmask_make()
        if not self.smask_ready():
            self.smask_ready()
        return True

    @staticmethod
    def copy_from()

    ## path
    @staticmethod
    def make_dir(path):
        if path == "" or path is None:
            return 
        if not isinstance(path,str):
            return 
        if not os.path.isdir(path):
            try: os.makedirs(path)
            except: pass

    def path_ready(self):
        if self.outDir is None or (not os.path.isdir(self.outDir)):
            return False
        if self.runDir is None or (not os.path.isdir(self.runDir)):
            return False
        return True

    def path_make(self):
        Setup.make_dir(self.outDir)
        Setup.make_dir(self.runDir)

    ## xtc
    def xtc_on(self):
        xtc_files = self.exp.find_xtc()
        if len(xtc_files) == 0:
            return False
        return True

    def xtc_ready(self):
        xtc_files = self.exp.find_xtc()
        if len(xtc_files) == 0:
            return True
        mtime = os.path.getmtime(sorted(xtc_files)[-1])
        ntime = time.time()
        if ntime - mtime > 120:
            return True
        return False

    ## calib
    def calib_ready(self):
        calib_file = self.exp.find_calib()
        if calib_file is None:
            return False
        return True

    def calib_make(self,dtype=None,**kwargs):
        if not isinstance(self.expName,str):
            return False
        if not isinstance(self.runNumber,int):
            return False
        if not isinstance(dtype,str):
            return False
        if dtype.lower() == "crystfel":
            if Setup.crystfel2calib(self.expName,self.runNumber,**kwargs):
                return True
        else:
            print "!! Not supported method"
        return False

    @staticmethod
    def crystfel2calib(expName,runNumber):
        return True


    ## geom
    def geom_ready(self):
        if self.fgeom is None or (not os.path.isfile(self.fgeom)):
            return False
        return True

    def geom_make(self):
        fcalib = self.exp.find_calib()
        if fcalib is None:
            return False
        detName = self.detName
        if detName is None:
            if self.exp.Det is None:
                return False
            detName = self.exp.detName
        if detName is None:
            return False
        fgeom = self.fgeom
        if fgeom is None:
            return False
        Setup.calib2crystfel(fcalib,detName,fgeom)

    @staticmethod
    def calib2crystfel(calibFile, detName, fsave):
        from psgeom import camera
        if 'cspad' in detName.lower():
            geom = camera.Cspad.from_psana_file(calibFile)
            geom.to_crystfel_file(fsave)
        elif 'rayonix' in detName.lower():
            geom = camera.CompoundAreaCamera.from_psana_file(calibFile)
            geom.to_crystfel_file(fsave)

    ## psana mask
    def pmask_ready(self):
        if self.pmask is None or (not os.path.isfile(self.pmask)):
            return False
        return True

    def pmask_make(self):
        if self.pmask is None or (not os.path.isfile(self.pmask)):
            return
        unassem_img = self.exp.pmask
        if unassem_img is None:
            return 
        np.save(self.pmask, self.exp.det.image(self.exp.evt,unassem_img))


    ## staticMask
    def smask_ready(self):
        if self.smask is None or (not os.path.isfile(self.smask)):
            return False
        return True

    def smask_make(self):
        if self.smask is None or (not os.path.isfile(self.smask)):
            return
        unassem_img = self.exp.pmask
        if unassem_img is None:
            return 
        if self.detName is None:
            self.exp.det 
            if self.detName is None:
                return 
            self.detName = self.exp.detName
        Setup.save_cheetah_mask(unassem_img, self.expName, self.detName, self.smask)
        return True

    @staticmethod
    def save_cheetah_mask(unassem_img, expName, detName, fsave):
        if 'cspad' in detName.lower() and 'cxi' in expName:
            dim0 = 8 * 185
            dim1 = 4 * 388
        elif 'rayonix' in detName.lower() and 'mfx' in expName:
            dim0 = 1920
            dim1 = 1920
        elif 'rayonix' in detName.lower() and 'xpp' in expName:
            dim0 = 1920
            dim1 = 1920
        else:
            print "saveCheetahFormatMask not implemented"
        myHdf5 = h5py.File(fsave, 'w')
        dset = myHdf5.create_dataset('/entry_1/data_1/mask', (dim0, dim1), dtype='int')

        # Convert calib image to cheetah image
        if True:
            img = np.zeros((dim0, dim1))
            counter = 0
            if 'cspad' in detName.lower() and 'cxi' in expName:
                for quad in range(4):
                    for seg in range(8):
                        img[seg * 185:(seg + 1) * 185, quad * 388:(quad + 1) * 388] = unassem_img[counter, :, :]
                        counter += 1
            elif 'rayonix' in detName.lower() and 'mfx' in expName:
                img = unassem_img[counter, :, :]  # psana format
            elif 'rayonix' in detName.lower() and 'xpp' in expName:
                img = unassem_img[counter, :, :]  # psana format

        dset[:, :] = img
        myHdf5.close()



    ## other setups 
    @staticmethod
    def deploy_calib(expName, runNumber, newCx, newCy, detName=None):
        ## deploy the new geometry file
        ## Calculate detector translation in x and y
        exp = myExp(expName,runNumber,detName)
        if exp.det is None:
            return 
        psanaCx, psanaCy = exp.det.point_indexes(exp.evt, pxy_um=(0, 0))
        pixelSize = exp.det.pixel_size(exp.evt)

        print "##### current psana center: ", psanaCx, psanaCy

        dx = pixelSize * (psanaCx - newCx)  # microns
        dy = pixelSize  * (psanaCy - newCy)  # microns
        geo = exp.det.geometry(exp.evt)

        if 'cspad' in exp.detName.lower() and 'cxi' in expName:
            geo.move_geo('CSPAD:V1', 0, dx=dx, dy=dy, dz=0)
        elif 'rayonix' in exp.detName.lower() and 'mfx' in expName:
            top = geo.get_top_geo()
            children = top.get_list_of_children()[0]
            geo.move_geo(children.oname, 0, dx=dx, dy=dy, dz=0)
        elif 'rayonix' in exp.detName.lower() and 'xpp' in expName:
            top = geo.get_top_geo()
            children = top.get_list_of_children()[0]
            geo.move_geo(children.oname, 0, dx=dx, dy=dy, dz=0)
        else:
            print "autoDeploy not implemented"

        params = myPath(expName, runNumber)
        fname = params.runDir + "/" + str(runNumber) + '-end.data'
        geo.save_pars_in_file(fname)
        print "#################################################"
        print "Deploying psana detector geometry: ", fname
        print "#################################################"
        cmts = {'exp': expName, 'app': 'psocake', 'comment': 'auto recentred geometry'}
        calibDir = '/reg/d/psdm/' + expName[:3] + '/' + expName +  '/calib'

        from PSCalib.CalibFileFinder import deploy_calib_file   
        deploy_calib_file(cdir=calibDir, src=str(exp.det.name), type='geometry', \
            run_start=int(runNumber), run_end=None, ifname=fname, dcmts=cmts, pbits=0)

