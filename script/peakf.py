import time
import os,sys
import subprocess
from core.experiment import Exp
from core.parameters import Path
from packg.util import WorkerBsubPsana,random_string,Command


class PeakFinder:
    def __init__(self,expName=None,runNumber=None,detName=None,outDir=None,exp=None,path=None,**kwargs):
        ## ncpus,noe,queue,
        """
        bsub -q psanaq -n 24 -o /reg/data/ana03/scratch/zhensu/expers/mfx13016/mfx13016/zhensu/psocake/r0031/.%J.log \
        -J hello mpirun findPeaks -e mfx13016 -d Rayonix \
        --outDir /reg/data/ana03/scratch/zhensu/expers/mfx13016/mfx13016/zhensu/psocake/r0031 \
        --algorithm 2 --alg_npix_min 2.0 --alg_npix_max 50.0 --alg_amax_thr 100.0 --alg_atot_thr 200.0 \
        --alg_son_min 7.0 --alg1_thr_low 0.0 --alg1_thr_high 0.0 --alg1_rank 3 --alg1_radius 3 --alg1_dr 2 \
        --psanaMask_on True --psanaMask_calib True --psanaMask_status True --psanaMask_edges True \
        --psanaMask_central True --psanaMask_unbond True --psanaMask_unbondnrs True \
        --mask /reg/data/ana03/scratch/zhensu/expers/mfx13016/mfx13016/zhensu/psocake/r0031/staticMask.h5 \
        --clen MFX:DET:MMS:04.RBV --coffset 0.0848 --minPeaks 15 --maxPeaks 2048 --minRes -1 \
        --sample sample --instrument MFX --pixelSize 8.9e-05 --auto False --detectorDistance 0.0848 \
        --access ana --tag testing -r 31 
        """
        self.exp  = exp  or Exp(expName,runNumber,detName) 
        self.path = path or Path(expName,runNumber,outDir) 
        self.submitry = False
        self.submitus = False

    def _queue(self):
        return self.kwargs.get("queue") or "psanaq"

    def _ncpus(self):
        return self.kwargs.get("ncpus") or 12

    def _flog(self):
        if hasattr(self,"flog"):
            return self.flog
        if self.kwargs.get("flog"):
            return self.kwargs.get("flog")
        self.flog = os.path.join(self.path.runDir,"./peakfinder_%s.log"%random_string(12))
        self.flog = os.path.realpath(self.flog)
        return self.flog

    def _jname(self):
        if hasattr(self,"jname"):
            return self.jname
        if self.kwargs.get("jname"):
            return self.kwargs.get("jname")
        self.jname = self.kwargs.get("jname") or random_string(12)
        return self.jname

    def _e(self):
        return self.exp.expName
    def _d(self):
        det = self.exp.Det
        return self.exp.detName
    def _outDir(self):
        return self.path.outDir

    def _algorithm(self):
        return self.kwargs.get("algorithm") or 2
    def _alg_npix_min(self):
        return self.kwargs.get("alg_npix_min") or 2.0
    def _alg_npix_max(self):
        return self.kwargs.get("alg_npix_max") or 50.0 
    def _alg_amax_thr(self):
        return self.kwargs.get("alg_amax_thr") or 100.0 
    def _alg_atot_thr(self):
        return self.kwargs.get("alg_atot_thr") or 200.0

    def _alg_son_min(self): 
        return self.kwargs.get("alg_son_min") or 7.0 
    def _alg1_thr_low(self): 
        return self.kwargs.get("alg1_thr_low") or 0.0 
    def _alg1_thr_high(self): 
        return self.kwargs.get("alg1_thr_high") or 0.0 
    def _alg1_rank(self): 
        return self.kwargs.get("alg1_rank") or 3 
    def _alg1_radius(self): 
        return self.kwargs.get("alg1_radius") or 3 
    def _alg1_dr(self): 
        return self.kwargs.get("alg1_dr") or 2

    def _psanaMask_on(self): 
        return self.kwargs.get("psanaMask_on") or True 
    def _psanaMask_calib(self): 
        return self.kwargs.get("psanaMask_calib") or True 
    def _psanaMask_status(self): 
        return self.kwargs.get("psanaMask_status") or True 
    def _psanaMask_edges(self): 
        return self.kwargs.get("psanaMask_edges") or True
    def _psanaMask_central(self): 
        return self.kwargs.get("psanaMask_central") or True 
    def _psanaMask_unbond(self): 
        return self.kwargs.get("psanaMask_unbond") or True 
    def _psanaMask_unbondnrs(self): 
        return self.kwargs.get("psanaMask_unbondnrs") or True

    def _mask(self):
        return self.kwargs.get("mask") or self.path.smask
    def userMask_path(self):
        return self.kwargs.get("userMask_path")
    def _clen(self): 
        return self.kwargs.get("clen") or self.exp.clenEpics
    def _coffset(self): 
        return self.kwargs.get("coffset") or self.exp.coffset
    def _minPeaks(self): 
        return self.kwargs.get("minPeaks") or 15 
    def _maxPeaks(self): 
        return self.kwargs.get("maxPeaks") or 2048 
    def _minRes(self): 
        return self.kwargs.get("minRes") or -1
    def _sample(self): 
        return self.kwargs.get("sample") or "sample"
    def _instrument(self): 
        return self.kwargs.get("instrument") or "MFX" 
    def _pixelSize(self): 
        return self.kwargs.get("pixelSize") or self.exp.pixelsize 
    def _auto(self): 
        return self.kwargs.get("auto") or False 
    def _detectorDistance(self): 
        return self.kwargs.get("detectorDistance") or self.exp.distance 

    def _access(self): 
        return self.kwargs.get("access") or "ana"
    def _tag(self): 
        return self.kwargs.get("tag") 
    def _r(self): 
        return self.kwargs.get("r") or self.exp.runNumber 
    def _noe(self):
        return self.kwargs.get("noe")

    def command(self):
        """
        bsub -q psanaq -n 24 -o /reg/data/ana03/scratch/zhensu/expers/mfx13016/mfx13016/zhensu/psocake/r0031/.%J.log \
        -J hello mpirun findPeaks -e mfx13016 -d Rayonix \
        --outDir /reg/data/ana03/scratch/zhensu/expers/mfx13016/mfx13016/zhensu/psocake/r0031 \
        --algorithm 2 --alg_npix_min 2.0 --alg_npix_max 50.0 --alg_amax_thr 100.0 --alg_atot_thr 200.0 \
        --alg_son_min 7.0 --alg1_thr_low 0.0 --alg1_thr_high 0.0 --alg1_rank 3 --alg1_radius 3 --alg1_dr 2 \
        --psanaMask_on True --psanaMask_calib True --psanaMask_status True --psanaMask_edges True \
        --psanaMask_central True --psanaMask_unbond True --psanaMask_unbondnrs True \
        --mask /reg/data/ana03/scratch/zhensu/expers/mfx13016/mfx13016/zhensu/psocake/r0031/staticMask.h5 \
        --clen MFX:DET:MMS:04.RBV --coffset 0.0848 --minPeaks 15 --maxPeaks 2048 --minRes -1 \
        --sample sample --instrument MFX --pixelSize 8.9e-05 --auto False --detectorDistance 0.0848 \
        --access ana --tag testing -r 31 
        """
        if not self.exp.Det:
            print "!! exp/run information is wrong"
            return None

        comm = Command("bsub")
        comm.args("-q",self._queue())
        comm.args("-n",self._ncpus())
        comm.args("-o",self._flog())
        comm.args("-J",self._jname())
        comm.add("mpirun findPeaks")
        comm.args("-e",self._e()) 
        comm.args("-d", self._d())
        comm.args("--outDir", self._outDir())

        comm.args("--algorithm", self._algorithm())
        comm.args("--alg_npix_min", self._alg_npix_min())
        comm.args("--alg_npix_max", self._alg_npix_max())
        comm.args("--alg_amax_thr", self._alg_amax_thr())
        comm.args("--alg_atot_thr", self._alg_atot_thr())
        comm.args("--alg_son_min", self._alg_son_min())
        comm.args("--alg1_thr_low", self._alg1_thr_low())
        comm.args("--alg1_thr_high", self._alg1_thr_high())
        comm.args("--alg1_rank", self._alg1_rank())
        comm.args("--alg1_radius", self._alg1_radius())
        comm.args("--alg1_dr", self._alg1_dr())
        comm.args("--noe",self._noe())

        comm.args("--psanaMask_on", self._psanaMask_on())
        comm.args("--psanaMask_calib", self._psanaMask_calib())
        comm.args("--psanaMask_status", self._psanaMask_status())
        comm.args("--psanaMask_edges", self._psanaMask_edges())
        comm.args("--psanaMask_central", self._psanaMask_central())
        comm.args("--psanaMask_unbond", self._psanaMask_unbond())
        comm.args("--psanaMask_unbondnrs", self._psanaMask_unbondnrs())
        comm.args("--mask", self._mask())
        comm.args("--userMask_path", self._userMask_path())

        comm.args("--clen", self._clen())
        comm.args("--coffset", self._coffset())
        comm.args("--minPeaks", self._minPeaks())
        comm.args("--maxPeaks", self._maxPeaks())
        comm.args("--minRes" , self._minRes())
        comm.args("--sample", self._sample())
        comm.args("--instrument", self._instrument())
        comm.args("--pixelSize", self._pixelSize())
        comm.args("--auto", self._auto())
        comm.args("--detectorDistance", self._detectorDistance())

        comm.args("--access", self._access())
        comm.args("--tag", self._tag())
        comm.args("--r", self._r())

        return comm.command()

    def launch(self):
        ## TODO: cases that submission failed
        comm = self.command()
        if comm is None:
            return False
        ## launch the command
        import shlex
        self.submitry = True
        try:
            p = subprocess.Popen(shlex.split(comm),stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            out,err = p.communicate()
            time.sleep(5)
        except Exception as err:
            print "!! err submission",err
            return False

        if err:
            print "!! err to submit jobs", err
            try: p.terminate()
            except: pass 
            try: p.kill()
            except: pass 
            return False

        import re
        jobid = re.findall("<(.*?)>",out)
        if len(jobid)==0:
            print "!! submission failed"
            try: p.terminate()
            except: pass 
            try: p.kill()
            except: pass
            return False

        self.submitus = True
        return True

    def status(self):
        if not self.submitry:
            return "waiting"
        if not self.submitus:
            return "failed"
        return WorkerBsubPsana.status_jobname(self._jname())

    def wait(self):
        import time
        start_time = time.time()
        while True:
            if time.time() - start_time > 3600.*5:
                return False
            _status = self.status()
            if _status in [None,"failed","terminated","killed","exit"]:
                return False
            if _status in ["done","waiting"]:
                return True
            time.sleep(2)

    def stop(self):
        if not self.submitry:
            return True
        if not self.submitus:
            return True
        jobids = WorkerBsubPsana.jobname2ids(self._jname())
        if len(jobids) == 0:
            return True
        for jobid in jobids:
            WorkerBsubPsana.killjob(jobid)
        return True
    
