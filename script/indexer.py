import time
import h5py
import os,sys
import numpy as np

PATH = os.path.realpath(__file__+"/../../")
if PATH not in sys.path:
    sys.path.append(PATH)
from script.util import WorkerBsubPsana as qmonitor
from script.util import random_string,Command

# TODO: slurm job status
class IndexPsana:
    def __init__(self,cxiList=None,lstList=None,fcell=None,outDir="./",fcrystfel=None,monitor=qmonitor,**kwargs):
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
        self.submitry = None
        self.submitus = None
        self.monitor  = monitor
        self.fcrystfel = fcrystfel
        self.fcell = fcell 
        if not os.path.isdir(outDir):
            self.outDir = os.path.realpath("./")
        else:
            self.outDir = os.path.realpath(outDir)
        self.kwargs = kwargs

    def _q(self):
        return self.kwargs.get("queue") or "psanaq"

    def _flog(self):
        if hasattr(self,"flog"):
            return self.flog
        if self.kwargs.get("flog"):
            return self.kwargs.get("flog")
        self.flog = os.path.join(self.outDir,"./indexer_%s.log"%random_string(12))
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
        if not self.lstList:
            self.lstList = IndexPsana.make_list(cxiList=self.cxiList,indextag=self.kwargs.get("indextag"),\
                    likelihood=self._likelihood(),chuckSize=self._chunkSize())
            return self.lstList
        return self.lstList

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

        stream_marker = self.kwargs.get("indextag") or random_string(12) 

        for idx,flst in enumerate(self._i()):
            comm = Command("bsub")
            comm.args("-q",self._q()) 
            comm.args("-o",self._flog()+"-%.4d"%idx)
            comm.args("-J",self._J())
            comm.add("-n 1 -x indexamajig -j '`nproc`'") 
            comm.args("-i",flst) 
            comm.args("-g", self._g())
            comm.add("--peaks=%s"%self._peaks())
            comm.add("--int-radius=%s"%self._int_radius())
            comm.add("--indexing=%s"%self._indexing())
            comm.args("-o", os.path.join(self.outDir, "%s_%.4d.stream"%(stream_marker,idx)) )
            comm.add("--temp-dir=%s"%self._temp_dir())
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
            from shutil import copyfile
            copyfile(self.fstreams[0], fstream)
        ## has multiple stream files
        print("## merge into: %s"%fstream)
        outfile = IndexPsana.stream_merge(streamList=self.fstreams,outDir=self.outDir,fstream=fstream,indextag=self.kwargs.get("indextag"))
        return outfile

    def launch(self):
        ## TODO: cases that submission failed
        commList = self.command()
        if commList is None:
            return False
        if len(commList)==0:
            return False

        self.submitry = [None for _ in commList]
        self.submitus = [None for _ in commList]
        self.jobids   = [None for _ in commList]
        if not os.path.isdir(self.outDir):
            os.makedirs(self.outDir)

        ## launch the command
        import shlex
        for idx,comm in enumerate(commList):
            try:
                import subprocess
                self.submitry[idx] = True
                p = subprocess.Popen(shlex.split(comm),stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                out,err = p.communicate()
                time.sleep(5)
            except Exception as err:
                print "!! err submission",err
                self.submitus[idx] = False
                return False

            # submitted but has error message
            if err:
                print "!! err to submit jobs", err
                try: p.terminate()
                except: pass 
                try: p.kill()
                except: pass 
                self.submitus[idx] = False
                return False

            import re
            jobid = re.findall("<(.*?)>",out)
            if len(jobid)==0:
                print "!! submission failed"
                try: p.terminate()
                except: pass 
                try: p.kill()
                except: pass
                self.submitus[idx] = False
                return False

            self.jobids[idx] = jobid
            self.submitus[idx] = True

        self.start_time = time.time()

    def status(self):
        # job not tried to submit
        if not self.submitry:
            return "waiting"
        # not all jobs tried to submit
        if not all(self.submitry):
            return "failed"
        # some jobs are failed in submission
        if not all(self.submitus):
            return "failed"
        # all jobs are submiited
        return self.monitor.status_jobname(self._J())

    def wait(self):
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
        # job not tried to submit
        if not self.submitry:
            return "waiting"
        for jobid in jobids:
            if jobid is None:
                break
            self.monitor.killjob(jobid)
        return True

    @staticmethod
    def stream_merge(streamList=[],outDir="./",fstream=None,indextag=None):
        ## merge multiple stream files
        if len(streamList)==0:
            return None
        if fstream is None:
            fstream = (indextag or random_string(12)) + ".stream"
            fstream = os.path.join(os.path.realpath(outDir),fstream)

        with open(fstream,"w") as fw:
            for fread in streamList:
                with open(fread,"r") as fr:
                    for line in fr:
                        fw.writelines(line)
        return fstream

    @staticmethod
    def make_list(cxiList=[],indextag=None,likelihood=0.,chuckSize=500):
        ## make **.lst files for indexamajig
        listfiles = []
        if len(cxiList) == 0:
            return listfiles

        marker = indextag or random_string(12)
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

