import time
import os,sys
import random
import string
import datetime
import subprocess


def random_string(N=20):
    return ''.join([random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(N)])

def date_string():
    return datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d-%H:%M:%S.%f')

def getusername(): 
    cmd = "whoami" 
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    out, err = process.communicate()
    return out

class WorkerBsubPsana:
    def __init__(self,actpack=None): 
        self.actpack = actpack 
        self.starttime = time.time() 
        self.submited = False 
        self.submitus = False 
        self.submitout = None 
        self.submiterr = None 
        self.__status__ = "waiting" 

    def start(self):
        command = self.makecmd()
        try:
            import shlex
            self.submited = True
            self.p = subprocess.Popen(shlex.split(command),stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            self.submitus = True
        except Exception as error:
            self.submiterr = error

    @staticmethod
    def findjobs(jobid=None,jobname=None,channel=""):
        # channel = "", "-d", "-p", "-r"
        if jobid is None and jobname is None:
            cmd = 'bjobs ' + channel + ' | grep ps'
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            out, err = process.communicate()
            try: process.kill()
            except: pass
            process.wait() 
        elif jobid is not None and jobname is None:
            cmd = "bjobs " + channel + " | grep " + str(jobid)
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            out, err = process.communicate()
            try: process.kill()
            except: pass
            process.wait() 
        elif jobid is None and jobname is not None:
            cmd = 'bjobs -J ' + '*\"' + jobname + '\"*' + ' ' + channel + ' | grep ps'
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            out, err = process.communicate()
            try: process.kill()
            except: pass
            process.wait() 
        elif jobid is not None and jobname is not None:
            cmd = 'bjobs -J ' + '*\"' + jobname + '\"*' + ' ' + channel + ' | grep ' + str(jobid)
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            out, err = process.communicate()
            try: process.kill()
            except: pass
            process.wait()
        return out
    
    @staticmethod
    def killjob(jobid):
        cmd = "bkill " + str(jobid)
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        out,err = process.communicate()
        try: process.kill()
        except: pass
        process.wait()
        return not err 

    @staticmethod
    def jobname2ids(jobname):
        jobids = []
        out = WorkerBsubPsana.findjobs(jobname=jobname)
        if not isinstance(out,str):
            return jobids
        for s in out.split("\n"):
            jobids.append(int(s.split()[0]))
        return jobids

    @staticmethod
    def status_jobname(jobname=None):
        # waiting,running,failed,terminated,done
        if jobname is None:
            return None
        # Check -d (done)
        out = WorkerBsubPsana.findjobs(jobname=jobname,channel="-d")
        partial_failed = False
        if "exit" in out:
            partial_failed = True
        ## check in incomplete jobs
        if partial_failed:
            return "failed"
        out = WorkerBsubPsana.findjobs(jobname=jobname)
        if len(out) == 0:
            return "done"
        return "running"

    @staticmethod
    def status_jobid(jobid=None):
        # waiting,running,failed,terminated,done,pending,suspended
        if jobid is None:
            return None 
        out = WorkerBsubPsana.findjobs(jobid=jobid) # None/RUN/PEND/SUS
#         print "find jobid bjobs", out
        if len(out) == 0:
            out3 = WorkerBsubPsana.findjobs(jobid=jobid,channel="-d")
#             print "find jobid bjobs -d", out3
            if len(out3) == 0:
                return "pending"
            if "done" in out3.lower():
                return "done"
            if "exit" in out3.lower():
                return "failed"
            return "terminated"
        if "susp" in out.lower():
            return "suspended"
        if "pend" in out.lower():
            return "pending"
        return "running"

    def status(self):
        if self.__status__ == "done":
            return "done"
        if not self.submited:
            return "waiting"
        if not self.submitus:
            return "failed"
        if self.p.poll() is None:
            return "running"
        elif self.p.poll() > 0:
            return "failed"
        elif self.p.poll() < 0:
            return "terminated"
        # it means p.poll() == 0: done
        if not hasattr(self,"jobid"):
            import re
            self.p.poll() 
            out,err = None,None
            try: out,err = self.p.communicate()
            except: pass
            self.submitout = self.submitout or out
            self.submiterr = self.submiterr or err
            jobid = re.findall("<(.*?)>",self.submitout)
            if len(jobid)==0:
                self.jobid = None
            else:
                self.jobid = int(jobid[0])
        if not hasattr(self,"jobname"):
            self.jobname = self.actpack.get("jobname") 
        if self.jobname:
            self.__status__ = WorkerBsubPsana.status_jobname(self.jobname)
            return self.__status__
        if self.jobid:
            self.__status__ = WorkerBsubPsana.status_jobid(self.jobid)
            return self.__status__
        return "noaccess"

    def ready(self):
        # waiting,running,pending,suspended,failed,terminated,done
        if self.status() not in ["running","waiting","pending","suspended"]:
            return True
        return False

    def success(self):
        if self.status() in ["done"]:
            return True
        return False

    def returned(self):
        if self.status() in [None,"running","waiting","pending","suspended"]:
            return {"return":None}
        elif self.status() in ["failed","terminate"]:
            out,err = None,None
            try: out,err = self.p.communicate()
            except: pass
            self.submitout = self.submitout or out
            self.submiterr = self.submiterr or err
            return {"out":self.submitout,"err":self.submiterr}
        elif self.status() in ["done"]:
            out,err = None,None
            try: out,err = self.p.communicate()
            except: pass
            self.submitout = self.submitout or out
            self.submiterr = self.submiterr or err
            return {"out":self.submitout,"err":self.submiterr}
        raise NotImplemented
    
    def jobreturn(self):
        if self.actpack.get("freturn") and self.status()=="done":
            import pickle
            return pickle.load(open(self.actpack.get("freturn"),"rb"))
        return None

    def wait(self):
        try: 
            out, err = self.p.communicate()
            self.submitout = out
            self.submiterr = err
        except: pass

    def close(self):
        WorkerBsubPsana.killjob(self.jobid)
        try: self.p.terminate()
        except: pass
        try: self.p.kill()
        except: pass
        try: self.p.wait()
        except: pass

    def clear(self):
        self.close()
        for key in self.__dict__:
            setattr(self,key,None)

    def runtime(self):
        return time.time() - self.starttime
        
    def _queue(self):
        return self.actpack.get("queue") or "psanaq"

    def _cpus(self):
        return self.actpack.get("cpus")  or 1

    def _pnode(self):
        nodes = self.actpack.get("nodes") or 1
        return int(math.ceil(self._cpus() * 1.0 / nodes))

    def _flog(self):
        if self.actpack.get("flog") is not None:
            return self.actpack.get("flog")
        self.actpack["flog"] = os.path.realpath(''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) \
                                                    for _ in range(20)) + ".out")
        return self.actpack.get("flog")

    def makecmd(self):
        if self.actpack.get("actobj").get("flaunch"):
            command = 'bsub -q %s -x -n %d -R "span[ptile=%d]" -o %s mpirun python %s'%(self._queue(),\
                    self._cpus(), self._pnode(), self._flog(), self.actpack.get("actobj").get("flaunch"))
            return command
        else: return self.actpack.get("actobj").get("command")
    

class Command:
    def __init__(self,initial=""):
        self.comm = initial
    
    def args(self,mark,value,ignore=[None,""]):
        if value in ignore:
            return self
        self.comm += " " + str(self.mark) + " " + str(value)
        return self

    def add(self,mark,ignore=[None,""]):
        if mark in ignore:
            return self
        self.comm += " " + str(mark)
        return self

    def command(self):
        return self.comm