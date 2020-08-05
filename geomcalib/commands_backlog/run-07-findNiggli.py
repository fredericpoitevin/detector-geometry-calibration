import os
import numpy as np
import subprocess
import evaluateIndexing as ei 
import sys
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-stream", "--stream", help="stream file", default=None, type=str)
parser.add_argument("-pdb", "--pdb", help="indexed with pdb or not", default="True", type=str)
args = parser.parse_args()


#sys.path.append("source /reg/g/cctbx/conda_build/build/setpaths.sh")


process = subprocess.Popen("find "+args.stream, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
out, err = process.communicate()
out = out.split('\n')

args.pdb = args.pdb.lower() in ["true", "yes", '1']

for streamfile in out:
    if not os.path.isfile(streamfile):
        continue 
    numIndex, numHits, indexHistogram = ei.getIndexHistogram(streamfile)
    lattice = indexHistogram[:,9:15].copy() 

    print "##### streamfile: ", streamfile
    print "##### with pdb? ", args.pdb
    print "##### numIndex/numHits: ", len(lattice),'/',numHits 
    if not args.pdb:
        #print lattice[:10], '\n'
        lattice = ei.check90(lattice)
        lattice = ei.convert2niggli(lattice)
        #print lattice[:10], '\n'
        [lattice, Volume] = ei.volumeFilter(lattice)
        #print lattice[:10], '\n'
        print "##### numIndex after filter: ", len(lattice)

    nuc = np.nanmean(lattice,axis=0).reshape((1,6))
    print "##### average cell: ", np.around(nuc,3)
    nuc = ei.check90(nuc)
    nuc = ei.convert2niggli(nuc).ravel()
    print "##### niggli cell: ", np.around(nuc,3)

