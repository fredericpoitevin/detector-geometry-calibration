from expParams import experiparams

class peakFinderHelper:
    def __init__(self, experimentName, runNumber, detectorName, outDir):
        self.experimentName = experimentName
        self.runNumber = runNumber
        self.detectorName = detectorName
        self.outDir = outDir

    def setDefaultParams(self):
        params = experiparams(self.experimentName, self.runNumber, detectorName=self.detectorName, outDir=self.outDir)
        params.setDefaultPsana()
        
        self.queue = 'psanaq'
        self.nodes = 1
        self.ncpus = 12
        self.outDir = params.cxiDir
        self.logFile = params.cxiDir+"/.%J.log"
        self.noe = -1
        self.jobName = "%s-r%.4d"%(params.experimentName, params.runNumber)

        ## peak finder algorithm params
        self.minPeaks = 15
        self.maxPeaks = 2048
        self.minRes = -1
        self.pkTag = ""
        
        ## mask params
        self.staticMask = params.cxiDir+'/staticMask.h5'
        self.userMask_path = None
        
        ## other params
        self.clen = params.clenEpics
        self.coffset = params.coffset 
        self.instrument = params.instrument
        self.pixelSize = params.pixelSize 
        self.detectorDistance = params.detectorDistance
        
        
# --clen MFX:DET:MMS:04.RBV 

    def getCommand(self):
        command = "bsub" + \
            " -q " + str(self.queue) + \
            " -n " + str(self.ncpus) + \
            " -o " + str(self.logFile) + \
            " -J " + str(self.jobName) + \
            " mpirun findPeaks " + \
            " -e " + str(self.experimentName) + \
            " -r " + str(self.runNumber) + \
            " -d " + str(self.detectorName) + \
            " --outDir " + str(self.outDir) + \
            " --algorithm " + str(self.algorithm) + \
            " --alg_npix_min " + str(self.alg_npix_min) + \
            " --alg_npix_max " + str(self.alg_npix_max) + \
            " --alg_amax_thr " + str(self.alg_amax_thr) + \
            " --alg_atot_thr " + str(self.alg_atot_thr) + \
            " --alg_son_min " + str(self.alg_son_min) + \
            " --alg1_thr_low " + str(self.alg1_thr_low) + \
            " --alg1_thr_high " + str(self.alg1_thr_high) + \
            " --alg1_rank " + str(self.alg1_rank) + \
            " --alg1_radius " + str(self.alg1_radius) + \
            " --alg1_dr " + str(self.alg1_dr) + \
            " --psanaMask_on " + "True" + \
            " --psanaMask_calib " + "True" + \
            " --psanaMask_status " + "True" + \
            " --psanaMask_edges " + "True" + \
            " --psanaMask_central " + "True" + \
            " --psanaMask_unbond " + "True" + \
            " --psanaMask_unbondnrs " + "True" + \
            " --mask " + str(self.staticMask) + \
            " --noe " + str(self.noe) + \
            " --clen " + str(self.clen) + \
            " --coffset " + str(self.coffset) + \
            " --minPeaks " + str(self.minPeaks) + \
            " --maxPeaks " + str(self.maxPeaks) + \
            " --minRes " + str(self.minRes) + \
            " --sample " + 'sample' + \
            " --instrument " + str(self.instrument) + \
            " --pixelSize " + str(self.pixelSize) + \
            " --auto False" + \
            " --detectorDistance " + str(self.detectorDistance) + \
            " --access ana"
            

        if self.pkTag is not None and self.pkTag != "":
            command += " --tag " + self.pkTag
        if self.userMask_path is not None:
            command += " --userMask_path " + str(self.userMask_path) 
            
        return command


    def setAdaptiveMode(self):
        self.algorithm = 2
        self.alg_npix_min = 2
        self.alg_npix_max = 30
        self.alg_amax_thr = 100
        self.alg_atot_thr = 150
        self.alg_son_min = 7
        self.alg1_thr_low = 0.
        self.alg1_thr_high = 0.
        self.alg1_rank = 3
        self.alg1_radius = 3
        self.alg1_dr = 2
        
        
    def setDropletMode(self):
        return 