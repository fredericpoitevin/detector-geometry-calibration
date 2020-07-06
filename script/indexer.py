import time
import os,sys
import subprocess
from core.experiment import Exp
from core.parameters import Path
from packg.util import WorkerBsubPsana,random_string,Command

# TODO: slurm job status

class IndexerServer:
    def __init__(self,cxiList=None,lstList=None,fcell=None,outDir=None,\
                fcrystfel=None,WorkerStatus=WorkerBsubPsana,**kwargs):
        ## ncpus,noe,queue,
        """
        bsub -q psanaq -o /reg/data/ana03/scratch/zhensu/expers/mfx13016/mfx13016/zhensu/psocake/r0037/.%J.log \
        -J mfx13016_37_1_nocell -n 1 -x indexamajig \
        -i /reg/data/ana03/scratch/zhensu/expers/mfx13016/mfx13016/zhensu/psocake/r0037/temp_mfx13016_37_1_nocell.lst \
        -j 'nproc' -g /reg/data/ana03/scratch/zhensu/expers/mfx13016/mfx13016/zhensu/psocake/r0031/.temp.geom \
        --peaks=cxi --int-radius=3,4,5 --indexing=mosflm,dirax \
        -o /reg/data/ana03/scratch/zhensu/expers/mfx13016/mfx13016/zhensu/psocake/r0037/temp_mfx13016_37_1_nocell.stream \
        --temp-dir=/scratch --tolerance=5,5,5,1.5 --no-revalidate --profile
        """
        self.cxiList  = cxiList
        self.lstList  = lstList
        self.submitry = False
        self.submitus = False

    def index_top_likelihood(N=10):
        # select with likelihood 
        return 

    def scan_center_detz(N=10):
        # scan every 3 pixels
        return 

    def _q(self):
        return self.kwargs.get("queue") or "psanaq"

    def _flog(self):
        if hasattr(self,"flog"):
            return self.flog
        if self.kwargs.get("flog"):
            return self.kwargs.get("flog")
        self.flog = os.path.join(self.path.runDir,"./peakfinder_%s.log"%random_string(12))
        self.flog = os.path.realpath(self.flog)
        return self.flog

    def _J(self):
        if hasattr(self,"jname"):
            return self.jname
        if self.kwargs.get("jname"):
            return self.kwargs.get("jname")
        self.jname = self.kwargs.get("jname") or random_string(12)
        return self.jname

    def _likelihood(self):
        return self.kwargs.get("likelihood") or 0.0

    def _chunkSize(self):
        return self.kwargs.get("chunkSize") or 500

    def _i(self):
        return self.lstList or Indexer.make_list(cxiList=self.cxiList,marker=None,\
                    likelihood=self._likelihood(),chuckSize=self._chunkSize()):

    def _g(self): 
        return self.fcrystfel

    def _peaks(self): 
        return self.kwargs.get("peaks") or "cxi" 

    def _int_radius(self): 
        return self.kwargs.get("int_radius") or "3,4,5" 

    def _indexing(self):
        return self.kwargs.get("indexing") or "mosflm,dirax"

    def _temp_dir(self):
        return self.kwargs.get("temp_dir") or "/scratch"

    def _tolerance(self):
        return self.kwargs.get("tolerance") or "5,5,5,1.5"

    def _pdb(self):
        return self.fcell

    def command(self):
        """
        bsub -q psanaq -o /reg/data/ana03/scratch/zhensu/expers/mfx13016/mfx13016/zhensu/psocake/r0037/.%J.log \
        -J mfx13016_37_1_nocell -n 1 -x indexamajig \
        -i /reg/data/ana03/scratch/zhensu/expers/mfx13016/mfx13016/zhensu/psocake/r0037/temp_mfx13016_37_1_nocell.lst \
        -j 'nproc' -g /reg/data/ana03/scratch/zhensu/expers/mfx13016/mfx13016/zhensu/psocake/r0031/.temp.geom \
        --peaks=cxi --int-radius=3,4,5 --indexing=mosflm,dirax \
        -o /reg/data/ana03/scratch/zhensu/expers/mfx13016/mfx13016/zhensu/psocake/r0037/temp_mfx13016_37_1_nocell.stream \
        --temp-dir=/scratch --tolerance=5,5,5,1.5 --pdb=/path --no-revalidate --profile
        """
        commList = []
        streamList = []
        if self._i() is None or len(self._i())==0:
            return commList
        marker = random_string(12)

        for idx,flst in enumerate(self._i()):
            comm = Command("bsub")
            comm.args("-q",self._q()) 
            comm.args("-o",self._flog())
            comm.args("-J",self._J())
            comm.add("-n 1 -x indexamajig -j '`nproc`'") 
            comm.args("-i",flst) 
            comm.args("-g", self._g())
            comm.add("--peaks=%s"%self._peaks())
            comm.add("--int-radius=%s"%self._int_radius())
            comm.add("--indexing=%s"%self._indexing())
            comm.args("-o", os.path.join(self.outDir or "./", "%s_%.3d.stream"%(self._J(),idx)) )
            comm.add("--temp-dir=%"%self._temp_dir())
            comm.add("--tolerance=%s"%self._tolerance())
            comm.add("--pdb=%s"%self._pdb())
            comm.add("--profile")
            comm.add("--no-revalidate")
            commList.append(comm.command())

        self.fstreams = streamList
        return commList

    def merge(self,fstream=None):
        if self.fstreams is None:
            return None
        if not isinstance(self.fstreams,list):
            return None
        if len(self.fstreams)<1:
            return None
        if len(self.fstreams)==1:
            if not fstreams:
                return self.fstreams[0]
            else:
                from shutil import copyfile
                copyfile(self.fstreams[0], fstream)
        ## has multiple stream files
        outfile = stream_merge(streamList=self.fstreams,outDir=self.outDir,fstream=fstream,marker=self.marker)
        return outfile


    def launchSingle(self):
        ## TODO: cases that submission failed
        commList = self.command()
        if commList is None:
            return False
        if len(commList)==0:
            return False
        ## launch the command
        import shlex

        self.submitry = True
        for comm in commList:
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

    @staticmethod
    def stream_merge(streamList=[],outDir="./",fstream=None,marker=None):
        ## merge multiple stream files
        if len(streamList)==0:
            return None
        if fstream is None:
            fstream = (marker or random_string(12)) + ".stream"
            fstream = os.path.join(os.path.realpath(outDir),fstream)

        with open(fstream,"w") as fw:
            for fread in streamList:
                with open(fread,"r") as fr:
                    for line in fr:
                        fw.writelines(line)
        return fstream

    @staticmethod
    def make_list(cxiList=[],marker=None,likelihood=0.,chuckSize=500):
        ## make **.lst files for indexamajig
        listfiles = []
        if len(cxiList) == 0:
            return listfiles

        marker = marker or random_string(12)
        dataline = []
        for fcxi in cxiList:
            if not os.path.isfile(fcxi):
                continue

            nImages = 0
            with h5py.File(fcxi,"r") as f:
                nImages = len(f["entry_1/data_1/data"])
                likeli = f["entry_1/result_1/likelihood"].value
                assert len(likeli)==nImages
            if nImages == 0:
                continue

            for idx in range(nImages):
                if likeli[idx] >= likelihood:
                    dataline.append("%s //%d\n"%(fcxi,idx))

        if len(dataline) == 0:
            return listfiles

        nfiles = len(dataline) * 1. / chuckSize
        if nfiles > int(nfiles):
            nfiles = int(nfiles) + 1
        else:
            nfiles = int(nfiles)

        for idxfile in range(nfiles):
            listfile = "%s_%.3d.lst"%(marker,idxfile)
            with open(listfile,"w") as f:
                f.writelines(dataline[(idxfile*chuckSize):((idxfile*chuckSize+chuckSize))])
            listfiles.append(listfile)
        return listfiles


class IndexerLocal:
    ## run command locally quickly
    def __init__(self):
        pass 

