import os
import shlex
import numpy as np
import subprocess
import evaluateIndexing as ei 
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-stream", "--stream", help="stream file", default=None, type=str)
parser.add_argument("-pdb", "--pdb", help="indexed with pdb or not", default="True", type=str) 
args = parser.parse_args()

    
process = subprocess.Popen("find " + args.stream, stdout=subprocess.PIPE, stderr=subprocess.PIPE,shell=True)
out, err = process.communicate()
print out
print err
out = out.split('\n')


print "Found stream", out
scores = []
for streamfile in out:
    if not os.path.isfile(streamfile):
        continue
    print "##### streamfile: ", streamfile
#     print "##### with pdb? ", bool(args.pdb.lower() in ["true", "yes", '1'])
    score = ei.evaluateIndexing(streamfile, withpdb=bool(args.pdb.lower() in ["true", "yes", '1']))
    print "##### score: ", score, "\n\n" #, np.sum(score[3:]), np.sum(score), score,'\n\n'
    
    scores.append(score or 0)
    
index = np.argmax(np.array(scores))
print "##### best stream file: ", out[index]