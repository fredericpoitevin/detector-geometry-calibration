import time
import os,sys
import subprocess
from core.experiment import Exp
from core.parameters import Path
from packg.util import WorkerBsubPsana,random_string,Command


class Powder:
    def __init__(self,expName=None,runNumber=None,detName=None,outDir=None,exp=None,path=None,**kwargs):
        ## ncpus,noe,queue,
        self.exp  = exp  or Exp(expName,runNumber,detName)
        self.path = path or Path(expName,runNumber,outDir)
        self.submitry = False
        self.submitus = False

    def _ncpus(self):
        return self.kwargs.get("ncpus") or 12

    def _jname(self):
        if hasattr(self,"jname"):
            return self.jname
        if self.kwargs.get("jname"):
            return self.kwargs.get("jname")
        self.jname = self.kwargs.get("jname") or random_string(12)
        return self.jname

    def _queue(self):
        return self.kwargs.get("queue") or "psanaq"

    def _tag(self):
        return self.kwargs.get("tag")

    def _exp(self):
        return self.exp.expName

    def _run(self):
        return self.exp.runNumber

    def _det(self):
        det = self.exp.Det
        return self.exp.detName

    def _noe(self):
        return self.kwargs.get("noe") or 3000

    def command(self):
        flaunch = os.path.realpath(__file__)
        flaunch = os.path.join(os.path.dirname(flaunch),"./scripts/powdersum.py")
        if not os.path.isfile(flaunch):
            print "!! File not exists"
            return None
        if not self.exp.Det:
            print "!! exp/run information is wrong"
            return None

        comm = Command("bsub")
        comm.args("-q",self._queue())
        comm.args("-n",self._ncpus())
        comm.args("-o",self._flog())
        comm.args("-J",self._jname())
        comm.args("mpirun python",flaunch)
        comm.args("--exp",self._exp())
        comm.args("--run",self._run())
        comm.args("--det",self._det())
        comm.args("--noe",self._noe())
        comm.args("--tag",self._tag())
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
            if time.time() - start_time > 3600.*2:
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
