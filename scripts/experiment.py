import psana
import os,sys
import numpy as np

class myExp(object):
    def __init__(self,expName=None,runNumber=None,detName=None):
        self.__expName__   = expName
        self.__runNumber__ = runNumber
        self.__detName__   = detName 
    
    def clean(self,keep=("__expName__","__runNumber__","__detName__","__epics__"),keepmore=()):
        for attr in self.__dict__.keys():
            if (attr not in keep) and (attr not in keepmore):
                delattr(self,attr)

    @property 
    def expName(self):
        if not hasattr(self,"__expName__"):
            self.__expName__ = None
        return self.__expName__

    @expName.setter
    def expName(self,value):
        if not hasattr(self,"__expName__"):
            self.__expName__ = value
        elif self.__expName__ is None:
            self.__expName__ = value
        elif self.__expName__ == value:
            pass
        else:
            self.clean()
            self.__expName__ = value

    @property 
    def runNumber(self):
        if not hasattr(self,"__runNumber__"):
            self.__runNumber__ = None
        return self.__runNumber__

    @runNumber.setter
    def runNumber(self,value):
        if not hasattr(self,"__runNumber__"):
            self.__runNumber__ = value
        elif self.__runNumber__ is None:
            self.__runNumber__ = value
        elif self.__runNumber__ == value:
            pass
        else:
            self.clean()
            self.__runNumber__ = value
    
    @property 
    def detName(self):
        if not hasattr(self,"__detName__"):
            self.__detName__ = None
        return self.__detName__

    @detName.setter
    def detName(self,value):
        if not hasattr(self,"__detName__"):
            self.__detName__ = value
        elif self.__detName__ is None:
            self.__detName__ = value
        elif self.__detName__ == value:
            pass
        else:
            self.clean(keepmore=("__ds__","__run__","__env__","__evt__"))
            self.__detName__ = value

    def get_ds(self):
        try:
            return psana.DataSource("exp="+self.expName+":run="+str(self.runNumber)+':idx')
        except Exception as err:
            print err
        return None

    @property 
    def ds(self):
        if not hasattr(self,"__ds__"):
            self.__ds__ = None
        if self.__ds__ is None:
            self.__ds__ = self.get_ds()
        return self.__ds__

    def get_run(self):
        try:
            return self.ds.runs().next()
        except Exception as err:
            print err 
        return None

    @property
    def run(self):
        if not hasattr(self,"__run__"):
            self.__run__ = None
        if self.__run__ is None:
            self.__run__ = self.get_run()
        return self.__run__

    def get_env(self):
        try:
            return self.ds.env()
        except Exception as err:
            print err
        return None

    @property
    def env(self):
        if not hasattr(self,"__env__"):
            self.__env__ = None
        if self.__env__ is None:
            self.__env__ = self.get_env()
        return self.__env__

    def get_evt(self):
        try:
            times = self.run.times()
            evt = None
            for counter in range(len(times)):
                evt = self.run.event(times[counter])
                if evt is not None:
                    break
            return evt
        except Exception as err:
            print err
        return None

    @property
    def evt(self):
        if not hasattr(self,"__evt__"):
            self.__evt__ = None
        if self.__evt__ is None:
            self.__evt__ = self.get_evt()
        return self.__evt__

    def get_epics(self):
        try:
            return self.ds.env().epicsStore()
        except Exception as err:
            print err
        return None

    @property
    def epics(self):
        if not hasattr(self,"__epics__"):
            self.__epics__ = None
        if self.__epics__ is None:
            self.__epics__ = self.get_epics()
        return self.__epics__

    def get_det_known(self):
        """
        return the det object with KNOWN detname,expname,runnumber
        """
        if self.detName is not None:
            try:
                ds = psana.DataSource("exp="+self.expName+":run="+str(self.runNumber)+':idx')  
                return psana.Detector(self.detName)
            except Exception as err:
                print err 
            return None
        return None

    def get_det_suggest(self):
        if not isinstance(self.expName,str):
            return []
        if not isinstance(self.runNumber,int):
            return []
        if self.ds is None:
            return []
        myAreaDetectors = []
        import Detector.PyDetector
        import Detector.AreaDetector
        ds = psana.DataSource("exp="+self.expName+":run="+str(self.runNumber)+':idx')
        for k in psana.DetNames():
            try:
                if Detector.PyDetector.dettype(str(k[0]), self.env) == Detector.AreaDetector.AreaDetector:
                    myAreaDetectors.append(k)
            except Exception as err:
                continue
        detInfoList = list(set(myAreaDetectors))
        return detInfoList

    @property
    def suggdets(self):
        if not hasattr(self,"__suggdets__"):
            self.__suggdets__ = None
        if self.__suggdets__ is None:
            self.__suggdets__ = self.get_det_suggest()
        return self.__suggdets__

    @property
    def det(self):
        if not hasattr(self,"__det__"):
            self.__det__ = None
        if self.__det__ is None:
            self.__det__ = self.get_det_known()
        return self.__det__

    def check_det(self,detName=None):
        if myExp(self.expName,self.runNumber,detName).distance is not None:
            return True
        return False

    def search_dets(self,detList=[]):
        """
        return the detName, not the det object
        """
        goodets = []
        for detlist in detList:
            if isinstance(detlist,str):
                detName = detlist[:]
                if self.check_det(detName):
                    goodets.append(detName)
            elif isinstance(detlist,(list,tuple,set)):
                for detName in detlist:
                    if not isinstance(detName,str):
                        continue
                    if self.check_det(detName):
                        goodets.append(detName)
        if len(goodets)==0:
            return None
        elif len(goodets)==1:
            return goodets[0]
        else:
            length = [len(_) for _ in goodets]
            argmin = length.index(min(length))
            return goodets[argmin]

    def get_Det(self):
        hasinfo = True
        trueinfo = True 
        if self.expName is None or self.runNumber is None:
            return None
        elif self.detName is None:
            hasinfo = False
        else:
            try: 
                if not self.det:
                    trueinfo = False
            except: 
                trueinfo = False

        if hasinfo and trueinfo:
            return self.det
        elif hasinfo and (not trueinfo): 
#             print "here"
            detName = self.search_dets(self.suggdets)
            if detName is not None:
                self.detName = detName
                return self.det
        elif (not hasinfo): 
#             print "hello"
            detName = self.search_dets(self.suggdets)
            if detName is not None:
                self.detName = detName
                return self.det
        return None

    @property
    def Det(self):
        if not hasattr(self,"__Det__"):
            self.__Det__ = None
        if self.__Det__ is None:
            self.__Det__ = self.get_Det()
        return self.__Det__

    def get_instrument(self):
        try:
            return self.det.instrument()
        except Exception as err:
            pass #print err 
        return None

    @property 
    def instrument(self):
        if not hasattr(self,"__instrument__"):
            self.__instrument__ = None
        if self.__instrument__ is None:
            self.__instrument__ = self.get_instrument()
        return self.__instrument__

    def get_clenEpics(self):
        if not isinstance(self.detName,str):
            return None
        if not isinstance(self.expName,str):
            return None
        if 'cspad2x2' in self.detName.lower():
            return None
        elif 'cspad' in self.detName.lower() and 'cxi' in self.expName:
            try:
                clenEpics = str(self.detName)+'_z'               
                clen = self.epics.value(clenEpics) / 1000.
                return clenEpics
            except:
                if 'ds1' in self.detName.lower():
                    clenEpics = str('CXI:DS1:MMS:06.RBV')
                    return clenEpics
                elif 'ds2' in self.detName.lower():
                    clenEpics = str('CXI:DS2:MMS:06.RBV')
                    return clenEpics 
                else:
                    print "!!!!! Couldn't handle detector clen."
                    return None
        elif ('rayonix' in self.detName.lower() and 'mfx' in self.expName) or \
                 ('cspad' in self.detName.lower() and 'mfx' in self.expName):
                clenEpics =  str('MFX:DET:MMS:04.RBV')
                return clenEpics
        return None

    @property 
    def clenEpics(self):
        if not hasattr(self,"__clenEpics__"):
            self.__clenEpics__ = None
        if self.__clenEpics__ is None:
            self.__clenEpics__ = self.get_clenEpics()
        return self.__clenEpics__

    def get_clen(self):
        if not isinstance(self.detName,str):
            return None
        if not isinstance(self.expName,str):
            return None
        if 'cspad2x2' in self.detName.lower():
            return 0.0
        elif 'cspad' in self.detName.lower() and 'cxi' in self.expName:
            try:
                clenEpics = str(self.detName)+'_z'               
                clen = self.epics.value(clenEpics) / 1000.
                return clen
            except:
                if 'ds1' in self.detName.lower():
                    clenEpics = str('CXI:DS1:MMS:06.RBV')
                    clen = self.epics.value(clenEpics) / 1000.
                    return clen
                elif 'ds2' in self.detName.lower():
                    clenEpics = str('CXI:DS2:MMS:06.RBV')
                    clen = self.epics.value(clenEpics) / 1000.
                    return clen
                else:
                    print "!!!!! Couldn't handle detector clen."
                    return None
        elif ('rayonix' in self.detName.lower() and 'mfx' in self.expName) or \
                 ('cspad' in self.detName.lower() and 'mfx' in self.expName):
                clenEpics =  str('MFX:DET:MMS:04.RBV')  
                try:
                    clen = self.epics.value(clenEpics) / 1000.
                    return clen
                except: 
#                     print "!!!!! ERROR: setting clen to 0.0 metre"
                    return 0.0
        return None

    @property 
    def clen(self):
        if not hasattr(self,"__clen__"):
            self.__clen__ = None
        if self.__clen__ is None:
            self.__clen__ = self.get_clen()
        return self.__clen__

    def get_distance(self):
        try:
            return np.mean(self.det.coords_z(self.evt))*1.0e-6
        except Exception as err:
            # print err
            pass
        return None

    @property
    def distance(self):
        if not hasattr(self,"__distance__"):
            self.__distance__ = None
        if self.__distance__ is None:
            self.__distance__ = self.get_distance()
        return self.__distance__

    def get_coffset(self):
        try:
            return self.distance - self.clen
        except Exception as err:
            print err
        return None

    @property
    def coffset(self):
        if not hasattr(self,"__coffset__"):
            self.__coffset__ = None
        if self.__coffset__ is None:
            self.__coffset__ = self.get_coffset()
        return self.__coffset__

    def get_pixelsize(self):
        try:
            return self.det.pixel_size(self.run)*1.0e-6
        except Exception as err:
            print err
        return None

    @property
    def pixelsize(self):
        if not hasattr(self,"__pixelsize__"):
            self.__pixelsize__ = None
        if self.__pixelsize__ is None:
            self.__pixelsize__ = self.get_pixelsize()
        return self.__pixelsize__

    def get_pmask(self):
        try:
            return self.det.mask(self.runNumber, \
                calib=True,status=True,edges=True,central=True,unbond=True,unbondnbrs=True)
        except Exception as err:
            print err
        return None

    @property
    def pmask(self):
        if not hasattr(self,"__pmask__"):
            self.__pmask__ = None
        if self.__pmask__ is None:
            self.__pmask__ = self.get_pmask()
        return self.__pmask__

    def get_center(self):
        try:
            return self.det.point_indexes(self.evt, pxy_um=(0, 0))
        except Exception as err:
            print err
        return None

    @property
    def center(self):
        if not hasattr(self,"__center__"):
            self.__center__ = None
        if self.__center__ is None:
            self.__center__ = self.get_center()
        return self.__center__

    def get_fcalib(self):
        if not isinstance(self.expName,str):
            return None 
        if not isinstance(self.runNumber,int):
            return None 
        if self.ds is None or self.det is None:
            return None 
        self.det.do_reshape_2d_to_3d(flag=True)
        calibFile = None 

        try:
            import Detector.PyDetector
            import PSCalib.GlobalUtils as gu
            source = Detector.PyDetector.map_alias_to_source(self.detName, self.ds.env())  # 'DetInfo(CxiDs2.0:Cspad.0)'
            calibSource = source.split('(')[-1].split(')')[0]  # 'CxiDs2.0:Cspad.0'
            detectorType = gu.det_type_from_source(source)  # 1
            calibGroup = gu.dic_det_type_to_calib_group[detectorType]  # 'CsPad::CalibV1'
        except:
            return calibFile

        if calibGroup is None or calibSource is None:
            return calibFile

        calibPath = "/reg/d/psdm/" + self.expName[0:3] + \
                         "/" + self.expName + "/calib/" + \
                         calibGroup + "/" + calibSource + "/geometry/"

        if not os.path.isdir(calibPath):
            return calibFile

        # Determine which calib file to use
        geometryFiles = os.listdir(calibPath)
        # print "geometry: \n " + "\n".join(geometryFiles) 
        minDiff = -1e6
        for fname in geometryFiles:
            if fname.endswith('.data'):
                endValid = False
                startNum = int(fname.split('-')[0])
                endNum = fname.split('-')[-1].split('.data')[0]
                diff = startNum - self.runNumber
                # Make sure it's end number is valid too
                if 'end' in endNum:
                    endValid = True
                else:
                    try:
                        if self.runNumber <= int(endNum):
                            endValid = True
                    except:
                        continue
                if diff <= 0 and diff > minDiff and endValid is True:
                    minDiff = diff
                    calibFile = calibPath + fname
        return calibFile

    @property
    def fcalib(self):
        if not hasattr(self,"__fcalib__"):
            self.__fcalib__ = None
        if self.__fcalib__ is None:
            self.__fcalib__ = self.get_fcalib()
        return self.__fcalib__

    def get_fxtc(self):
        if not isinstance(self.expName,str):
            return []
        if not isinstance(self.runNumber,int):
            return []
        import glob
        xtc_path = "/reg/d/psdm/%s/%s/xtc"%(self.expName[:3],self.expName)
        xtc_files = glob.glob(os.path.join(xtc_path,'*-r%.4d-*.xtc'%self.runNumber))
        return sorted(xtc_files)

    @property
    def fxtc(self):
        if not hasattr(self,"__fxtc__"):
            self.__fxtc__ = None
        if self.__fxtc__ is None:
            self.__fxtc__ = self.get_fxtc()
        return self.__fxtc__
